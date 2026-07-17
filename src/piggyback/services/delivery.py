"""Delivery backends for e-cards and postal fulfilment."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from importlib import import_module

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone

from piggyback.conf import get_setting
from piggyback.models import Delivery, DeliveryMethod, DeliveryStatus

logger = logging.getLogger(__name__)


class DeliveryBackend(ABC):
    @abstractmethod
    def send(self, delivery: Delivery) -> bool:
        ...


class EmailDeliveryBackend(DeliveryBackend):
    """Send personalised e-cards via email with a view link."""

    def send(self, delivery: Delivery) -> bool:
        item = delivery.order_item
        recipient = item.recipient
        if not recipient or not recipient.email:
            delivery.status = DeliveryStatus.FAILED
            delivery.error_message = "Recipient has no email address."
            delivery.save(update_fields=["status", "error_message", "updated_at"])
            return False

        view_url = self._build_view_url(delivery)
        context = {
            "recipient": recipient,
            "card": item.card,
            "sender": item.order.user,
            "view_url": view_url,
            "inside_message": item.card.inside_message,
        }
        sender_name = item.order.user.get_full_name() or item.order.user.username
        subject = f"You've received a card from {sender_name}!"
        text_body = render_to_string("piggyback/email/ecard.txt", context)
        html_body = render_to_string("piggyback/email/ecard.html", context)

        from_email = get_setting("DEFAULT_FROM_EMAIL") or settings.DEFAULT_FROM_EMAIL
        msg = EmailMultiAlternatives(subject, text_body, from_email, [recipient.email])
        msg.attach_alternative(html_body, "text/html")
        msg.send(fail_silently=False)

        delivery.mark_sent()
        delivery.status = DeliveryStatus.DELIVERED
        delivery.delivered_at = timezone.now()
        delivery.save(update_fields=["status", "delivered_at", "updated_at"])
        return True

    def _build_view_url(self, delivery: Delivery) -> str:
        base = getattr(settings, "PIGGYBACK_PUBLIC_URL", "http://localhost:8000")
        return f"{base.rstrip('/')}/cards/view/{delivery.view_token}/"


class PostalDeliveryBackend(DeliveryBackend):
    """Stub postal fulfilment — queues for print partner integration."""

    def send(self, delivery: Delivery) -> bool:
        item = delivery.order_item
        recipient = item.recipient
        if not recipient or not recipient.has_postal_address:
            delivery.status = DeliveryStatus.FAILED
            delivery.error_message = "Recipient has no complete postal address."
            delivery.save(update_fields=["status", "error_message", "updated_at"])
            return False

        delivery.status = DeliveryStatus.PROCESSING
        delivery.tracking_reference = f"PB-{delivery.id:08d}"
        delivery.save(update_fields=["status", "tracking_reference", "updated_at"])
        logger.info(
            "Postal card queued: delivery=%s recipient=%s ref=%s",
            delivery.id,
            recipient.full_name,
            delivery.tracking_reference,
        )
        delivery.mark_sent()
        return True


def get_backend(method: str) -> DeliveryBackend:
    backend_path = {
        DeliveryMethod.ECARD: get_setting("ECARD_DELIVERY_BACKEND"),
        DeliveryMethod.POST: get_setting("POSTAL_DELIVERY_BACKEND"),
        DeliveryMethod.PRINT_AT_HOME: get_setting("ECARD_DELIVERY_BACKEND"),
    }.get(method, get_setting("ECARD_DELIVERY_BACKEND"))

    module_path, class_name = backend_path.rsplit(".", 1)
    module = import_module(module_path)
    return getattr(module, class_name)()


def fulfil_delivery(delivery: Delivery) -> bool:
    method = delivery.order_item.delivery_method
    backend = get_backend(method)
    return backend.send(delivery)


def fulfil_order(order) -> list[Delivery]:
    """Process all pending deliveries for a paid order."""
    results = []
    for item in order.items.select_related("delivery", "card", "recipient"):
        delivery = getattr(item, "delivery", None)
        if delivery and delivery.status in (
            DeliveryStatus.PENDING,
            DeliveryStatus.SCHEDULED,
        ):
            if delivery.scheduled_for and delivery.scheduled_for > timezone.now():
                delivery.status = DeliveryStatus.SCHEDULED
                delivery.save(update_fields=["status", "updated_at"])
                continue
            fulfil_delivery(delivery)
            results.append(delivery)
    return results
