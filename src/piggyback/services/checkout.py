"""Pricing and checkout helpers."""

from piggyback.conf import get_setting
from piggyback.models import DeliveryMethod, GiftAddon, Order, OrderItem


def price_for_delivery(method: str) -> int:
    if method == DeliveryMethod.ECARD:
        return get_setting("ECARD_PRICE")
    if method == DeliveryMethod.POST:
        return get_setting("POSTED_CARD_PRICE")
    return 0


def add_card_to_cart(
    user,
    card,
    recipient=None,
    delivery_method=DeliveryMethod.ECARD,
    gift_addon: GiftAddon | None = None,
    gift_wrap: bool = False,
) -> OrderItem:
    order, _ = Order.objects.get_or_create(
        user=user,
        status=Order.OrderStatus.CART,
        defaults={},
    )
    unit_price = price_for_delivery(delivery_method)
    item = OrderItem.objects.create(
        order=order,
        card=card,
        recipient=recipient,
        delivery_method=delivery_method,
        gift_addon=gift_addon,
        gift_wrap=gift_wrap,
        unit_price_pence=unit_price,
    )
    order.recalculate_totals()
    return item


def checkout_order(order: Order, promo_code: str = "") -> Order:
    order.promo_code = promo_code
    if promo_code.upper() == "FIRSTCARD":
        order.discount_pence = min(order.subtotal_pence, 299)
    order.status = Order.OrderStatus.PENDING_PAYMENT
    order.recalculate_totals()
    order.save()
    return order


def complete_payment(order: Order) -> Order:
    from piggyback.models import Delivery, DeliveryStatus
    from piggyback.services.delivery import fulfil_order

    order.mark_paid()
    order.status = Order.OrderStatus.FULFILLING
    order.save(update_fields=["status", "updated_at"])

    for item in order.items.all():
        Delivery.objects.get_or_create(
            order_item=item,
            defaults={"status": DeliveryStatus.PENDING},
        )

    fulfil_order(order)
    order.status = Order.OrderStatus.COMPLETED
    order.save(update_fields=["status", "updated_at"])
    return order
