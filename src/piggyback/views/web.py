from django.contrib.auth import get_user_model
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView, ListView, TemplateView, View

from piggyback.adapters import get_user_details, sync_user_recipient
from piggyback.conf import get_setting
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
    Recipient,
    Reminder,
)
from piggyback.services.card_renderer import canvas_data_from_template, default_blank_canvas
from piggyback.services.checkout import checkout_order, complete_payment

User = get_user_model()


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
        else:
            if request.user.is_authenticated:
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


class LibraryView(ListView):
    template_name = "piggyback/library.html"
    context_object_name = "entries"
    paginate_by = 20

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


class RecipientsView(ListView):
    template_name = "piggyback/recipients.html"
    context_object_name = "recipients"

    def get_queryset(self):
        if get_setting("AUTO_SYNC_USER_RECIPIENT"):
            sync_user_recipient(self.request.user)
        return Recipient.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["system_user_details"] = get_user_details(self.request.user)
        return ctx


class CartView(View):
    template_name = "piggyback/cart.html"

    def get(self, request):
        order = None
        if request.user.is_authenticated:
            order, _ = Order.objects.get_or_create(
                user=request.user,
                status=Order.OrderStatus.CART,
            )
        gifts = GiftAddon.objects.filter(is_active=True)
        return render(request, self.template_name, {"order": order, "gifts": gifts})

    def post(self, request):
        action = request.POST.get("action")
        order = get_object_or_404(
            Order,
            user=request.user,
            status=Order.OrderStatus.CART,
        )
        if action == "checkout":
            checkout_order(order, request.POST.get("promo_code", ""))
            return redirect("piggyback:checkout", uuid=order.uuid)
        return redirect("piggyback:cart")


class CheckoutView(View):
    template_name = "piggyback/checkout.html"

    def get(self, request, uuid):
        order = get_object_or_404(Order, uuid=uuid, user=request.user)
        return render(request, self.template_name, {"order": order})

    def post(self, request, uuid):
        order = get_object_or_404(Order, uuid=uuid, user=request.user)
        complete_payment(order)
        return redirect("piggyback:order_confirmation", uuid=order.uuid)


class OrderConfirmationView(DetailView):
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


class RemindersView(ListView):
    template_name = "piggyback/reminders.html"
    context_object_name = "reminders"

    def get_queryset(self):
        return Reminder.objects.filter(user=self.request.user).select_related("recipient")
