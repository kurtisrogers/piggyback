from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from piggyback.adapters import get_user_details, sync_user_recipient, user_has_active_subscription
from piggyback.api.serializers import (
    AddToCartSerializer,
    CardLibraryEntrySerializer,
    CardSerializer,
    CardTemplateSerializer,
    CheckoutSerializer,
    CheckoutSessionSerializer,
    DeliverySerializer,
    DesignAssetSerializer,
    GiftAddonSerializer,
    OccasionCategorySerializer,
    OccasionSerializer,
    OrderSerializer,
    RecipientSerializer,
    ReminderSerializer,
    SubscriptionPlanSerializer,
    SubscriptionSerializer,
    UserDetailsSerializer,
)
from piggyback.conf import get_setting
from piggyback.models import (
    Card,
    CardLibraryEntry,
    CardStatus,
    CardTemplate,
    Delivery,
    DeliveryStatus,
    DesignAsset,
    GiftAddon,
    Occasion,
    OccasionCategory,
    Order,
    Recipient,
    Reminder,
    Subscription,
    SubscriptionPlan,
)
from piggyback.services.card_renderer import save_card_preview
from piggyback.services.checkout import add_card_to_cart, checkout_order, complete_payment
from piggyback.services.payments import get_payment_backend


class OccasionCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OccasionCategory.objects.prefetch_related("occasions")
    serializer_class = OccasionCategorySerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"


class OccasionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Occasion.objects.select_related("category")
    serializer_class = OccasionSerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"
    filterset_fields = ["category"]


class CardTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CardTemplate.objects.filter(is_active=True).select_related("occasion")
    serializer_class = CardTemplateSerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"
    filterset_fields = ["occasion", "style", "is_premium"]

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def personalize(self, request, slug=None):
        template = self.get_object()
        card = Card.objects.create(
            owner=request.user,
            template=template,
            occasion=template.occasion,
            title=f"My {template.name}",
            canvas_data=template.canvas_data,
            status=CardStatus.DRAFT,
        )
        return Response(
            CardSerializer(card, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class DesignAssetViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DesignAsset.objects.all()
    serializer_class = DesignAssetSerializer
    permission_classes = [AllowAny]
    filterset_fields = ["asset_type"]


class CardViewSet(viewsets.ModelViewSet):
    serializer_class = CardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Card.objects.filter(owner=self.request.user).select_related("template", "occasion")

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=["post"])
    def save_design(self, request, pk=None):
        card = self.get_object()
        card.canvas_data = request.data.get("canvas_data", card.canvas_data)
        card.inside_message = request.data.get("inside_message", card.inside_message)
        card.title = request.data.get("title", card.title)
        card.status = CardStatus.SAVED
        card.save()
        save_card_preview(card)
        return Response(CardSerializer(card, context={"request": request}).data)

    @action(detail=True, methods=["post"])
    def favorite(self, request, pk=None):
        card = self.get_object()
        card.is_favorite = not card.is_favorite
        card.save(update_fields=["is_favorite", "updated_at"])
        return Response({"is_favorite": card.is_favorite})


class CardLibraryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CardLibraryEntrySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = CardLibraryEntry.objects.filter(user=self.request.user).select_related("card")
        entry_type = self.request.query_params.get("type")
        if entry_type:
            qs = qs.filter(entry_type=entry_type)
        return qs


class RecipientViewSet(viewsets.ModelViewSet):
    serializer_class = RecipientSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if get_setting("AUTO_SYNC_USER_RECIPIENT"):
            sync_user_recipient(self.request.user)
        return Recipient.objects.filter(owner=self.request.user)

    def perform_destroy(self, instance):
        if instance.is_system_user:
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied("The synced system user entry cannot be deleted.")
        instance.delete()


class MeViewSet(viewsets.ViewSet):
    """Current user's system profile details from the host Django app."""

    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get"])
    def details(self, request):
        details = get_user_details(request.user)
        payload = UserDetailsSerializer(
            {
                **details.as_recipient_defaults(),
                "full_name": details.full_name,
            }
        ).data
        return Response(payload)

    @action(detail=False, methods=["get"])
    def subscription(self, request):
        sub = (
            Subscription.objects.filter(user=request.user)
            .select_related("plan")
            .order_by("-created_at")
            .first()
        )
        if sub is None:
            return Response({"active": False, "subscription": None})
        return Response(
            {
                "active": sub.is_active,
                "has_premium": user_has_active_subscription(request.user),
                "subscription": SubscriptionSerializer(sub).data,
            }
        )

    @action(detail=False, methods=["post"])
    def sync_recipient(self, request):
        recipient = sync_user_recipient(request.user)
        if recipient is None:
            return Response(
                {"detail": "System user sync is disabled."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(RecipientSerializer(recipient).data)


class GiftAddonViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = GiftAddon.objects.filter(is_active=True)
    serializer_class = GiftAddonSerializer
    permission_classes = [AllowAny]


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "uuid"

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("items")

    @action(detail=False, methods=["get"])
    def cart(self, request):
        order, _ = Order.objects.get_or_create(user=request.user, status=Order.OrderStatus.CART)
        return Response(OrderSerializer(order).data)

    @action(detail=False, methods=["post"])
    def add_to_cart(self, request):
        ser = AddToCartSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        card = Card.objects.get(pk=data["card_id"], owner=request.user)
        recipient = None
        if data.get("recipient_id"):
            recipient = Recipient.objects.get(pk=data["recipient_id"], owner=request.user)
        gift_addon = None
        if data.get("gift_addon_id"):
            gift_addon = GiftAddon.objects.get(pk=data["gift_addon_id"])
        item = add_card_to_cart(
            request.user,
            card,
            recipient=recipient,
            delivery_method=data["delivery_method"],
            gift_addon=gift_addon,
            gift_wrap=data["gift_wrap"],
        )
        if data.get("scheduled_for"):
            from piggyback.models import Delivery

            delivery, _ = Delivery.objects.get_or_create(order_item=item)
            delivery.scheduled_for = data["scheduled_for"]
            delivery.status = DeliveryStatus.SCHEDULED
            delivery.save()
        return Response(OrderSerializer(item.order).data)

    @action(detail=True, methods=["post"])
    def checkout(self, request, uuid=None):
        order = self.get_object()
        ser = CheckoutSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        order = checkout_order(order, ser.validated_data.get("promo_code", ""))
        return Response(OrderSerializer(order).data)

    @action(detail=True, methods=["post"])
    def pay(self, request, uuid=None):
        order = self.get_object()
        if order.status != Order.OrderStatus.PENDING_PAYMENT:
            return Response({"detail": "Order is not awaiting payment."}, status=400)

        backend = get_payment_backend()
        if backend.provider_name == "demo":
            order = complete_payment(order)
            return Response(OrderSerializer(order).data)

        success_url = request.data.get("success_url") or get_setting("STRIPE_ORDER_SUCCESS_URL")
        cancel_url = request.data.get("cancel_url") or get_setting("STRIPE_ORDER_CANCEL_URL")
        if not success_url or not cancel_url:
            return Response(
                {"detail": "success_url and cancel_url are required for Stripe checkout."},
                status=400,
            )
        session = backend.create_order_checkout_session(order, success_url, cancel_url)
        return Response(CheckoutSessionSerializer(session).data)


class DeliveryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DeliverySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Delivery.objects.filter(
            order_item__order__user=self.request.user,
        ).select_related("order_item")


class ReminderViewSet(viewsets.ModelViewSet):
    serializer_class = ReminderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Reminder.objects.filter(user=self.request.user).select_related(
            "recipient", "occasion"
        )


class SubscriptionPlanViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SubscriptionPlan.objects.filter(is_active=True)
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"


class SubscriptionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user).select_related("plan")

    @action(detail=False, methods=["post"])
    def checkout(self, request):
        if not get_setting("SUBSCRIPTION_ENABLED"):
            return Response({"detail": "Subscriptions are disabled."}, status=400)

        plan_slug = request.data.get("plan_slug")
        plan = SubscriptionPlan.objects.filter(slug=plan_slug, is_active=True).first()
        if plan is None:
            return Response({"detail": "Subscription plan not found."}, status=404)

        backend = get_payment_backend()
        success_url = request.data.get("success_url") or get_setting(
            "STRIPE_SUBSCRIPTION_SUCCESS_URL"
        )
        cancel_url = request.data.get("cancel_url") or get_setting("STRIPE_SUBSCRIPTION_CANCEL_URL")
        if not success_url or not cancel_url:
            return Response(
                {"detail": "success_url and cancel_url are required."},
                status=400,
            )

        if backend.provider_name == "demo":
            Subscription.objects.update_or_create(
                user=request.user,
                plan=plan,
                stripe_subscription_id=f"demo_sub_{request.user.pk}_{plan.slug}",
                defaults={
                    "stripe_customer_id": f"demo_cus_{request.user.pk}",
                    "status": Subscription.Status.ACTIVE,
                },
            )
            return Response({"checkout_url": success_url, "provider": "demo"})

        session = backend.create_subscription_checkout_session(
            request.user, plan, success_url, cancel_url
        )
        return Response(CheckoutSessionSerializer(session).data)

    @action(detail=False, methods=["post"])
    def portal(self, request):
        backend = get_payment_backend()
        return_url = request.data.get("return_url") or get_setting(
            "STRIPE_BILLING_PORTAL_RETURN_URL"
        )
        if not return_url:
            return Response({"detail": "return_url is required."}, status=400)
        session = backend.create_billing_portal_session(request.user, return_url)
        return Response(session)
