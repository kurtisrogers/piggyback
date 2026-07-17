import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

from piggyback.models.base import TimeStampedModel
from piggyback.models.cards import Card
from piggyback.models.recipients import Recipient


class DeliveryMethod(models.TextChoices):
    ECARD = "ecard", "E-Card (Email)"
    POST = "post", "Posted Card"
    PRINT_AT_HOME = "print", "Print at Home"


class DeliveryStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    SCHEDULED = "scheduled", "Scheduled"
    PROCESSING = "processing", "Processing"
    SENT = "sent", "Sent"
    DELIVERED = "delivered", "Delivered"
    FAILED = "failed", "Failed"
    CANCELLED = "cancelled", "Cancelled"


class GiftAddon(TimeStampedModel):
    """Optional gifts to include with posted cards."""

    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="piggyback/gifts/", blank=True)
    price_pence = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Order(TimeStampedModel):
    """Checkout order for one or more card deliveries."""

    class OrderStatus(models.TextChoices):
        CART = "cart", "Cart"
        PENDING_PAYMENT = "pending", "Pending Payment"
        PAID = "paid", "Paid"
        FULFILLING = "fulfilling", "Fulfilling"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"
        REFUNDED = "refunded", "Refunded"

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="piggyback_orders",
    )
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.CART,
    )
    subtotal_pence = models.PositiveIntegerField(default=0)
    discount_pence = models.PositiveIntegerField(default=0)
    total_pence = models.PositiveIntegerField(default=0)
    currency = models.CharField(max_length=3, default="GBP")
    paid_at = models.DateTimeField(null=True, blank=True)
    promo_code = models.CharField(max_length=40, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order {self.uuid} ({self.get_status_display()})"

    def recalculate_totals(self):
        self.subtotal_pence = sum(item.line_total_pence for item in self.items.all())
        self.total_pence = max(0, self.subtotal_pence - self.discount_pence)
        self.save(update_fields=["subtotal_pence", "total_pence", "updated_at"])

    def mark_paid(self):
        self.status = self.OrderStatus.PAID
        self.paid_at = timezone.now()
        self.save(update_fields=["status", "paid_at", "updated_at"])


class OrderItem(TimeStampedModel):
    """A card + delivery configuration within an order."""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name="order_items")
    recipient = models.ForeignKey(
        Recipient,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_items",
    )
    delivery_method = models.CharField(
        max_length=10,
        choices=DeliveryMethod.choices,
        default=DeliveryMethod.ECARD,
    )
    gift_addon = models.ForeignKey(
        GiftAddon,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_items",
    )
    gift_wrap = models.BooleanField(default=False)
    unit_price_pence = models.PositiveIntegerField(default=0)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.card.title} → {self.recipient or 'TBD'}"

    @property
    def line_total_pence(self):
        total = self.unit_price_pence * self.quantity
        if self.gift_wrap:
            total += 199
        if self.gift_addon:
            total += self.gift_addon.price_pence
        return total


class Delivery(TimeStampedModel):
    """Tracks fulfilment of a single card delivery."""

    order_item = models.OneToOneField(
        OrderItem,
        on_delete=models.CASCADE,
        related_name="delivery",
    )
    status = models.CharField(
        max_length=20,
        choices=DeliveryStatus.choices,
        default=DeliveryStatus.PENDING,
    )
    scheduled_for = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    tracking_reference = models.CharField(max_length=100, blank=True)
    error_message = models.TextField(blank=True)
    view_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    class Meta:
        verbose_name_plural = "deliveries"

    def __str__(self):
        return f"Delivery for {self.order_item}"

    def mark_sent(self):
        self.status = DeliveryStatus.SENT
        self.sent_at = timezone.now()
        self.save(update_fields=["status", "sent_at", "updated_at"])
        self.order_item.card.mark_sent()
