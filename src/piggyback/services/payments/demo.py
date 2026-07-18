"""Demo payment backend when Stripe is not configured."""

from piggyback.services.payments.base import PaymentBackend


class DemoPaymentBackend(PaymentBackend):
    provider_name = "demo"

    def is_configured(self) -> bool:
        return True

    def create_order_checkout_session(self, order, success_url: str, cancel_url: str) -> dict:
        return {
            "provider": "demo",
            "checkout_url": success_url,
            "session_id": f"demo_order_{order.uuid}",
        }

    def create_subscription_checkout_session(
        self, user, plan, success_url: str, cancel_url: str
    ) -> dict:
        return {
            "provider": "demo",
            "checkout_url": success_url,
            "session_id": f"demo_subscription_{user.pk}_{plan.slug}",
        }

    def create_billing_portal_session(self, user, return_url: str) -> dict:
        return {"provider": "demo", "portal_url": return_url}

    def handle_webhook(self, payload: bytes, signature: str) -> None:
        return None
