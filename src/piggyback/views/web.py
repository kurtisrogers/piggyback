from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import DetailView, ListView, TemplateView

from piggyback.adapters import get_user_details, sync_user_recipient
from piggyback.conf import get_setting
from piggyback.forms import RecipientForm, ReminderForm
from piggyback.models import (
    Card,
    CardLibraryEntry,
    CardStatus,
    CardStyle,
    CardTemplate,
    Delivery,
    GiftAddon,
    Occasion,
    OccasionCategory,
    Order,
    OrderItem,
    Recipient,
    Reminder,
)
from piggyback.services.card_renderer import canvas_data_from_template, default_blank_canvas
from piggyback.services.checkout import add_card_to_cart, checkout_order, complete_payment
from piggyback.views.htmx import is_htmx

User = get_user_model()


def _recipient_panel_context(request):
    if get_setting("AUTO_SYNC_USER_RECIPIENT"):
        sync_user_recipient(request.user)
    return {
        "recipients": Recipient.objects.filter(owner=request.user),
        "form": RecipientForm(),
    }


def _reminder_panel_context(request):
    return {
        "reminders": Reminder.objects.filter(user=request.user).select_related("recipient"),
        "form": ReminderForm(request.user),
    }


def _cart_context(request):
    order, _ = Order.objects.get_or_create(
        user=request.user,
        status=Order.OrderStatus.CART,
    )
    return {
        "order": order,
        "gifts": GiftAddon.objects.filter(is_active=True),
    }


class HomeView(TemplateView):
    template_name = "piggyback/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["featured_categories"] = OccasionCategory.objects.filter(is_featured=True)[:6]
        ctx["popular_templates"] = CardTemplate.objects.filter(is_active=True).order_by(
            "-popularity_score"
        )[:8]
        return ctx


class CatalogView(ListView):
    template_name = "piggyback/catalog.html"
    context_object_name = "templates"
    paginate_by = 24

    def get_template_names(self):
        if is_htmx(self.request):
            return ["piggyback/partials/template_grid.html"]
        return [self.template_name]

    def get_queryset(self):
        qs = CardTemplate.objects.filter(is_active=True).select_related("occasion")
        occasion_slug = self.request.GET.get("occasion")
        style = self.request.GET.get("style")
        if occasion_slug:
            qs = qs.filter(occasion__slug=occasion_slug)
        if style:
            qs = qs.filter(style=style)
        return qs.order_by("-popularity_score")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categories"] = OccasionCategory.objects.annotate(
            template_count=Count("occasions__templates")
        )
        ctx["occasions"] = Occasion.objects.select_related("category")
        ctx["selected_occasion"] = self.request.GET.get("occasion", "")
        ctx["selected_style"] = self.request.GET.get("style", "")
        ctx["card_styles"] = CardStyle.choices
        return ctx


class EditorView(View):
    template_name = "piggyback/editor.html"

    def get(self, request, card_id=None, template_slug=None):
        card = None
        template = None
        if card_id:
            if not request.user.is_authenticated:
                return redirect(f"/admin/login/?next={request.path}")
            card = get_object_or_404(Card, pk=card_id, owner=request.user)
        elif template_slug:
            template = get_object_or_404(CardTemplate, slug=template_slug, is_active=True)
            if request.user.is_authenticated:
                card = Card.objects.create(
                    owner=request.user,
                    template=template,
                    occasion=template.occasion,
                    title=f"My {template.name}",
                    canvas_data=canvas_data_from_template(template),
                    status=CardStatus.DRAFT,
                )
        elif request.user.is_authenticated:
            card = Card.objects.create(
                owner=request.user,
                title="Blank Card",
                canvas_data=default_blank_canvas(),
                status=CardStatus.DRAFT,
            )

        return render(
            request,
            self.template_name,
            {"card": card, "template": template},
        )


class EditorSendModalView(LoginRequiredMixin, View):
    def get(self, request, card_id):
        card = get_object_or_404(Card, pk=card_id, owner=request.user)
        if get_setting("AUTO_SYNC_USER_RECIPIENT"):
            sync_user_recipient(request.user)
        recipients = Recipient.objects.filter(owner=request.user)
        gifts = GiftAddon.objects.filter(is_active=True)
        return render(
            request,
            "piggyback/partials/send_card_modal.html",
            {"card": card, "recipients": recipients, "gifts": gifts},
        )


class EditorSendView(LoginRequiredMixin, View):
    def post(self, request, card_id):
        card = get_object_or_404(Card, pk=card_id, owner=request.user)
        recipient = None
        recipient_id = request.POST.get("recipient_id")
        if recipient_id:
            recipient = get_object_or_404(Recipient, pk=recipient_id, owner=request.user)

        gift_addon = None
        gift_addon_id = request.POST.get("gift_addon_id")
        if gift_addon_id:
            gift_addon = get_object_or_404(GiftAddon, pk=gift_addon_id)

        add_card_to_cart(
            request.user,
            card,
            recipient=recipient,
            delivery_method=request.POST.get("delivery_method", "ecard"),
            gift_addon=gift_addon,
            gift_wrap=request.POST.get("gift_wrap") == "true",
        )
        return HttpResponse(status=204)


class LibraryView(LoginRequiredMixin, ListView):
    template_name = "piggyback/library.html"
    context_object_name = "entries"
    paginate_by = 20

    def get_template_names(self):
        if is_htmx(self.request):
            return ["piggyback/partials/library_grid.html"]
        return [self.template_name]

    def get_queryset(self):
        qs = CardLibraryEntry.objects.filter(user=self.request.user).select_related("card")
        entry_type = self.request.GET.get("type")
        if entry_type:
            qs = qs.filter(entry_type=entry_type)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["filter_type"] = self.request.GET.get("type", "")
        return ctx


class LibraryFavoriteView(LoginRequiredMixin, View):
    def post(self, request, card_id):
        card = get_object_or_404(Card, pk=card_id, owner=request.user)
        card.is_favorite = not card.is_favorite
        card.save(update_fields=["is_favorite", "updated_at"])
        return HttpResponse(status=204)


class RecipientsView(LoginRequiredMixin, ListView):
    template_name = "piggyback/recipients.html"
    context_object_name = "recipients"

    def get_queryset(self):
        if get_setting("AUTO_SYNC_USER_RECIPIENT"):
            sync_user_recipient(self.request.user)
        return Recipient.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["system_user_details"] = get_user_details(self.request.user)
        ctx["form"] = RecipientForm()
        return ctx


class RecipientCreateView(LoginRequiredMixin, View):
    def post(self, request):
        form = RecipientForm(request.POST)
        if form.is_valid():
            recipient = form.save(commit=False)
            recipient.owner = request.user
            recipient.save()
            return render(
                request,
                "piggyback/partials/recipients_panel.html",
                _recipient_panel_context(request),
            )
        return render(
            request,
            "piggyback/partials/recipients_panel.html",
            {**_recipient_panel_context(request), "form": form},
            status=400,
        )


class RecipientDeleteView(LoginRequiredMixin, View):
    def delete(self, request, pk):
        recipient = get_object_or_404(Recipient, pk=pk, owner=request.user)
        if recipient.is_system_user:
            return HttpResponse("Cannot delete synced profile.", status=403)
        recipient.delete()
        return render(
            request,
            "piggyback/partials/recipients_panel.html",
            _recipient_panel_context(request),
        )


class RemindersView(LoginRequiredMixin, ListView):
    template_name = "piggyback/reminders.html"
    context_object_name = "reminders"

    def get_queryset(self):
        return Reminder.objects.filter(user=self.request.user).select_related("recipient")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["form"] = ReminderForm(self.request.user)
        return ctx


class ReminderCreateView(LoginRequiredMixin, View):
    def post(self, request):
        form = ReminderForm(request.user, request.POST)
        if form.is_valid():
            reminder = form.save(commit=False)
            reminder.user = request.user
            reminder.save()
            return render(
                request,
                "piggyback/partials/reminders_panel.html",
                _reminder_panel_context(request),
            )
        return render(
            request,
            "piggyback/partials/reminders_panel.html",
            {**_reminder_panel_context(request), "form": form},
            status=400,
        )


class ReminderDeleteView(LoginRequiredMixin, View):
    def delete(self, request, pk):
        reminder = get_object_or_404(Reminder, pk=pk, user=request.user)
        reminder.delete()
        return render(
            request,
            "piggyback/partials/reminders_panel.html",
            _reminder_panel_context(request),
        )


class CartView(LoginRequiredMixin, View):
    template_name = "piggyback/cart.html"

    def get(self, request):
        return render(request, self.template_name, _cart_context(request))

    def post(self, request):
        action = request.POST.get("action")
        order = get_object_or_404(
            Order,
            user=request.user,
            status=Order.OrderStatus.CART,
        )
        if action == "apply_promo":
            promo = request.POST.get("promo_code", "")
            order.promo_code = promo
            order.discount_pence = (
                min(order.subtotal_pence, 299) if promo.upper() == "FIRSTCARD" else 0
            )
            order.recalculate_totals()
            if is_htmx(request):
                return render(
                    request,
                    "piggyback/partials/cart_content.html",
                    _cart_context(request),
                )
        if action == "checkout":
            checkout_order(order, request.POST.get("promo_code", ""))
            return redirect("piggyback:checkout", uuid=order.uuid)
        return redirect("piggyback:cart")


class CartRemoveView(LoginRequiredMixin, View):
    def delete(self, request, item_id):
        item = get_object_or_404(
            OrderItem,
            pk=item_id,
            order__user=request.user,
            order__status=Order.OrderStatus.CART,
        )
        order = item.order
        item.delete()
        order.recalculate_totals()
        return render(
            request,
            "piggyback/partials/cart_content.html",
            _cart_context(request),
        )


class CheckoutView(LoginRequiredMixin, View):
    template_name = "piggyback/checkout.html"

    def get(self, request, uuid):
        order = get_object_or_404(Order, uuid=uuid, user=request.user)
        return render(request, self.template_name, {"order": order})

    def post(self, request, uuid):
        order = get_object_or_404(Order, uuid=uuid, user=request.user)
        complete_payment(order)
        return redirect("piggyback:order_confirmation", uuid=order.uuid)


class OrderConfirmationView(LoginRequiredMixin, DetailView):
    template_name = "piggyback/order_confirmation.html"
    context_object_name = "order"
    slug_field = "uuid"
    slug_url_kwarg = "uuid"

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class CardViewView(View):
    """Public e-card viewing page (via delivery token)."""

    template_name = "piggyback/card_view.html"

    def get(self, request, token):
        delivery = get_object_or_404(Delivery, view_token=token)
        card = delivery.order_item.card
        return render(
            request,
            self.template_name,
            {"card": card, "delivery": delivery, "sender": delivery.order_item.order.user},
        )
