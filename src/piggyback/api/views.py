from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from piggyback.api.serializers import (
    AddToCartSerializer,
    CardLibraryEntrySerializer,
    CardSerializer,
    CardTemplateSerializer,
    CheckoutSerializer,
    DeliverySerializer,
    DesignAssetSerializer,
    GiftAddonSerializer,
    OccasionCategorySerializer,
    OccasionSerializer,
    OrderSerializer,
    RecipientSerializer,
    ReminderSerializer,
)
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
)
from piggyback.services.card_renderer import save_card_preview
from piggyback.services.checkout import add_card_to_cart, checkout_order, complete_payment


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
        return Recipient.objects.filter(owner=self.request.user)


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
        order = complete_payment(order)
        return Response(OrderSerializer(order).data)


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
