"""Payment backend abstraction."""

from __future__ import annotations

from importlib import import_module

from piggyback.conf import get_setting


class PaymentBackend:
    """Create checkout sessions and handle provider webhooks."""

    provider_name = "base"

    def is_configured(self) -> bool:
        return False

    def create_order_checkout_session(self, order, success_url: str, cancel_url: str) -> dict:
        raise NotImplementedError

    def create_subscription_checkout_session(
        self, user, plan, success_url: str, cancel_url: str
    ) -> dict:
        raise NotImplementedError

    def create_billing_portal_session(self, user, return_url: str) -> dict:
        raise NotImplementedError

    def handle_webhook(self, payload: bytes, signature: str) -> None:
        raise NotImplementedError


def get_payment_backend() -> PaymentBackend:
    if not get_setting("STRIPE_SECRET_KEY") and get_setting("DEMO_PAYMENTS"):
        from piggyback.services.payments.demo import DemoPaymentBackend

        return DemoPaymentBackend()

    backend_path = get_setting("PAYMENT_BACKEND")
    module_path, class_name = backend_path.rsplit(".", 1)
    module = import_module(module_path)
    backend_cls = getattr(module, class_name)
    return backend_cls()
