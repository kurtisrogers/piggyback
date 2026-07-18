"""Stripe payment backend for one-time orders and subscriptions."""

from __future__ import annotations

from django.utils import timezone

from piggyback.adapters.billing import get_billing_adapter, set_stripe_customer_id
from piggyback.conf import get_setting
from piggyback.models import Order, Subscription, SubscriptionPlan
from piggyback.services.checkout import complete_payment
from piggyback.services.payments.base import PaymentBackend


def _stripe():
    try:
        import stripe
    except ImportError as exc:
        raise RuntimeError("Install stripe: pip install pypiggyback[stripe]") from exc

    stripe.api_key = get_setting("STRIPE_SECRET_KEY")
    return stripe


class StripePaymentBackend(PaymentBackend):
    provider_name = "stripe"

    def is_configured(self) -> bool:
        return bool(get_setting("STRIPE_SECRET_KEY"))

    def _get_or_create_customer(self, user) -> str:
        adapter = get_billing_adapter()
        identity = adapter.get_billing_identity(user)
        if identity.stripe_customer_id:
            return identity.stripe_customer_id

        stripe = _stripe()
        customer = stripe.Customer.create(
            email=identity.email or None,
            name=identity.name or None,
            metadata={"user_id": str(user.pk)},
        )
        set_stripe_customer_id(user, customer.id)
        return customer.id

    def create_order_checkout_session(self, order, success_url: str, cancel_url: str) -> dict:
        stripe = _stripe()
        customer_id = self._get_or_create_customer(order.user)

        line_items = [
            {
                "price_data": {
                    "currency": order.currency.lower(),
                    "unit_amount": order.total_pence,
                    "product_data": {
                        "name": f"Piggyback order {order.uuid}",
                        "description": f"{order.items.count()} card(s)",
                    },
                },
                "quantity": 1,
            }
        ]

        session = stripe.checkout.Session.create(
            mode="payment",
            customer=customer_id,
            line_items=line_items,
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "order_uuid": str(order.uuid),
                "user_id": str(order.user_id),
                "checkout_type": "order",
            },
        )

        order.stripe_checkout_session_id = session.id
        order.payment_provider = self.provider_name
        order.save(update_fields=["stripe_checkout_session_id", "payment_provider", "updated_at"])

        return {
            "provider": self.provider_name,
            "checkout_url": session.url,
            "session_id": session.id,
            "publishable_key": get_setting("STRIPE_PUBLISHABLE_KEY"),
        }

    def create_subscription_checkout_session(
        self, user, plan: SubscriptionPlan, success_url: str, cancel_url: str
    ) -> dict:
        stripe = _stripe()
        customer_id = self._get_or_create_customer(user)

        if not plan.stripe_price_id:
            raise ValueError(f"Subscription plan '{plan.slug}' has no stripe_price_id configured.")

        session = stripe.checkout.Session.create(
            mode="subscription",
            customer=customer_id,
            line_items=[{"price": plan.stripe_price_id, "quantity": 1}],
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "user_id": str(user.pk),
                "plan_slug": plan.slug,
                "checkout_type": "subscription",
            },
        )

        return {
            "provider": self.provider_name,
            "checkout_url": session.url,
            "session_id": session.id,
            "publishable_key": get_setting("STRIPE_PUBLISHABLE_KEY"),
        }

    def create_billing_portal_session(self, user, return_url: str) -> dict:
        stripe = _stripe()
        customer_id = self._get_or_create_customer(user)
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=return_url,
        )
        return {"provider": self.provider_name, "portal_url": session.url}

    def handle_webhook(self, payload: bytes, signature: str) -> None:
        stripe = _stripe()
        webhook_secret = get_setting("STRIPE_WEBHOOK_SECRET")
        if not webhook_secret:
            raise ValueError("PIGGYBACK_STRIPE_WEBHOOK_SECRET is not configured.")

        event = stripe.Webhook.construct_event(payload, signature, webhook_secret)

        if event.type == "checkout.session.completed":
            self._handle_checkout_completed(event.data.object)
        elif event.type == "customer.subscription.updated":
            self._handle_subscription_updated(event.data.object)
        elif event.type == "customer.subscription.deleted":
            self._handle_subscription_deleted(event.data.object)

    def _handle_checkout_completed(self, session) -> None:
        metadata = session.get("metadata") or {}
        checkout_type = metadata.get("checkout_type")

        if checkout_type == "order":
            order_uuid = metadata.get("order_uuid")
            if not order_uuid:
                return
            try:
                order = Order.objects.get(uuid=order_uuid)
            except Order.DoesNotExist:
                return
            if order.status == Order.OrderStatus.PAID:
                return
            order.stripe_payment_intent_id = session.get("payment_intent") or ""
            order.stripe_checkout_session_id = session.get("id") or ""
            order.payment_provider = self.provider_name
            order.save(
                update_fields=[
                    "stripe_payment_intent_id",
                    "stripe_checkout_session_id",
                    "payment_provider",
                    "updated_at",
                ]
            )
            if order.status == Order.OrderStatus.PENDING_PAYMENT:
                complete_payment(order)
            return

        if checkout_type == "subscription":
            self._sync_subscription_from_stripe(session.get("subscription"), metadata)

    def _handle_subscription_updated(self, stripe_subscription) -> None:
        self._upsert_subscription(stripe_subscription)

    def _handle_subscription_deleted(self, stripe_subscription) -> None:
        sub_id = stripe_subscription.get("id")
        Subscription.objects.filter(stripe_subscription_id=sub_id).update(
            status=Subscription.Status.CANCELED,
            canceled_at=timezone.now(),
        )

    def _sync_subscription_from_stripe(self, subscription_id: str | None, metadata: dict) -> None:
        if not subscription_id:
            return
        stripe = _stripe()
        stripe_subscription = stripe.Subscription.retrieve(subscription_id)
        self._upsert_subscription(stripe_subscription, metadata)

    def _upsert_subscription(self, stripe_subscription, metadata: dict | None = None) -> None:
        from django.contrib.auth import get_user_model

        User = get_user_model()
        metadata = metadata or stripe_subscription.get("metadata") or {}
        user_id = metadata.get("user_id")
        plan_slug = metadata.get("plan_slug")

        if not user_id:
            customer_id = stripe_subscription.get("customer")
            from piggyback.models import BillingProfile

            profile = BillingProfile.objects.filter(stripe_customer_id=customer_id).first()
            if profile:
                user_id = profile.user_id

        if not user_id:
            return

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return

        price_id = ""
        items = stripe_subscription.get("items", {}).get("data", [])
        if items:
            price_id = items[0].get("price", {}).get("id", "")

        plan = None
        if plan_slug:
            plan = SubscriptionPlan.objects.filter(slug=plan_slug).first()
        if plan is None and price_id:
            plan = SubscriptionPlan.objects.filter(stripe_price_id=price_id).first()
        if plan is None:
            return

        status = stripe_subscription.get("status", Subscription.Status.INCOMPLETE)
        Subscription.objects.update_or_create(
            stripe_subscription_id=stripe_subscription["id"],
            defaults={
                "user": user,
                "plan": plan,
                "stripe_customer_id": stripe_subscription.get("customer", ""),
                "status": status,
                "current_period_start": _ts(stripe_subscription.get("current_period_start")),
                "current_period_end": _ts(stripe_subscription.get("current_period_end")),
                "cancel_at_period_end": stripe_subscription.get("cancel_at_period_end", False),
                "canceled_at": _ts(stripe_subscription.get("canceled_at")),
            },
        )


def _ts(value):
    from datetime import timezone as dt_timezone

    if not value:
        return None
    return timezone.datetime.fromtimestamp(value, tz=dt_timezone.utc)
