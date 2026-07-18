import json
from unittest.mock import MagicMock, patch

import pytest
from django.urls import reverse

from piggyback.adapters.billing import DefaultBillingAdapter, set_stripe_customer_id
from piggyback.models import (
    BillingProfile,
    Card,
    CardTemplate,
    Occasion,
    OccasionCategory,
    Order,
    Subscription,
    SubscriptionPlan,
)
from piggyback.services.checkout import add_card_to_cart, checkout_order
from piggyback.services.payments.demo import DemoPaymentBackend


@pytest.fixture
def category(db):
    return OccasionCategory.objects.create(name="Birthday", slug="birthday", icon="🎂")


@pytest.fixture
def occasion(category):
    return Occasion.objects.create(name="Birthday", slug="birthday-general", category=category)


@pytest.fixture
def template(occasion):
    return CardTemplate.objects.create(
        name="Birthday Classic",
        slug="birthday-classic",
        occasion=occasion,
        canvas_data={"background": "#FFF8F0", "objects": []},
    )


@pytest.fixture
def card(user, template):
    return Card.objects.create(
        owner=user,
        template=template,
        title="Test Card",
        canvas_data=template.canvas_data,
    )


@pytest.fixture
def recipient(user):
    from piggyback.models import Recipient

    return Recipient.objects.create(
        owner=user,
        first_name="Bob",
        last_name="Smith",
        email="bob@example.com",
    )


@pytest.fixture
def subscription_plan(db):
    return SubscriptionPlan.objects.create(
        name="Premium",
        slug="premium",
        description="Premium templates and assets",
        amount_pence=499,
        interval=SubscriptionPlan.Interval.MONTH,
    )


@pytest.mark.django_db
class TestBillingAdapter:
    def test_fallback_billing_profile_created(self, user):
        set_stripe_customer_id(user, "cus_test_123")
        profile = BillingProfile.objects.get(user=user)
        assert profile.stripe_customer_id == "cus_test_123"
        assert profile.billing_email == user.email

    def test_get_billing_identity_from_fallback(self, user):
        BillingProfile.objects.create(
            user=user,
            stripe_customer_id="cus_existing",
            billing_email="billing@example.com",
            billing_name="Alice Anderson",
        )
        adapter = DefaultBillingAdapter()
        identity = adapter.get_billing_identity(user)
        assert identity.stripe_customer_id == "cus_existing"
        assert identity.email == "billing@example.com"
        assert identity.name == "Alice Anderson"


@pytest.mark.django_db
class TestDemoPaymentBackend:
    def test_order_checkout_demo(self, user, card, recipient):
        item = add_card_to_cart(user, card, recipient=recipient)
        order = checkout_order(item.order, "")
        backend = DemoPaymentBackend()
        session = backend.create_order_checkout_session(
            order,
            "http://example.com/success",
            "http://example.com/cancel",
        )
        assert session["provider"] == "demo"
        assert "demo_order_" in session["session_id"]

    def test_subscription_checkout_demo(self, user, subscription_plan):
        backend = DemoPaymentBackend()
        session = backend.create_subscription_checkout_session(
            user,
            subscription_plan,
            "http://example.com/success",
            "http://example.com/cancel",
        )
        assert session["provider"] == "demo"
        assert subscription_plan.slug in session["session_id"]


@pytest.mark.django_db
class TestSubscriptionAPI:
    def test_list_plans(self, api_client, subscription_plan):
        response = api_client.get("/api/subscriptions/plans/")
        assert response.status_code == 200
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["slug"] == "premium"

    def test_demo_subscription_checkout(self, api_client, user, subscription_plan):
        response = api_client.post(
            "/api/subscriptions/checkout/",
            {
                "plan_slug": "premium",
                "success_url": "http://example.com/success",
                "cancel_url": "http://example.com/cancel",
            },
            format="json",
        )
        assert response.status_code == 200
        assert response.data["provider"] == "demo"
        assert Subscription.objects.filter(user=user, plan=subscription_plan).exists()

    def test_me_subscription(self, api_client, user, subscription_plan):
        Subscription.objects.create(
            user=user,
            plan=subscription_plan,
            stripe_subscription_id="demo_sub_1",
            status=Subscription.Status.ACTIVE,
        )
        response = api_client.get("/api/me/subscription/")
        assert response.status_code == 200
        assert response.data["active"] is True
        assert response.data["has_premium"] is True


@pytest.mark.django_db
class TestOrderPaymentAPI:
    def test_demo_pay(self, api_client, user, card, recipient):
        item = add_card_to_cart(user, card, recipient=recipient)
        order = checkout_order(item.order, "")
        response = api_client.post(f"/api/orders/{order.uuid}/pay/")
        assert response.status_code == 200
        order.refresh_from_db()
        assert order.status == Order.OrderStatus.COMPLETED


@pytest.mark.django_db
class TestStripeWebhook:
    def test_webhook_rejects_missing_secret(self, client, settings):
        settings.PIGGYBACK_STRIPE_SECRET_KEY = "sk_test_fake"
        settings.PIGGYBACK_DEMO_PAYMENTS = False
        response = client.post(
            reverse("piggyback:stripe_webhook"),
            data=b"{}",
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="sig",
        )
        assert response.status_code == 400

    @patch("piggyback.services.payments.stripe._stripe")
    def test_webhook_completes_order(self, mock_stripe_fn, client, user, card, recipient, settings):
        settings.PIGGYBACK_STRIPE_SECRET_KEY = "sk_test_fake"
        settings.PIGGYBACK_STRIPE_WEBHOOK_SECRET = "whsec_test"
        settings.PIGGYBACK_DEMO_PAYMENTS = False

        item = add_card_to_cart(user, card, recipient=recipient)
        order = checkout_order(item.order, "")

        mock_stripe = MagicMock()
        mock_stripe_fn.return_value = mock_stripe
        event = MagicMock()
        event.type = "checkout.session.completed"
        event.data.object = {
            "id": "cs_test",
            "payment_intent": "pi_test",
            "metadata": {
                "checkout_type": "order",
                "order_uuid": str(order.uuid),
            },
        }
        mock_stripe.Webhook.construct_event.return_value = event

        response = client.post(
            reverse("piggyback:stripe_webhook"),
            data=json.dumps({}),
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="sig",
        )
        assert response.status_code == 200
        order.refresh_from_db()
        assert order.status == Order.OrderStatus.COMPLETED
        assert order.payment_provider == "stripe"


@pytest.mark.django_db
class TestSubscriptionWebViews:
    def test_subscriptions_page(self, client, user, subscription_plan):
        client.force_login(user)
        response = client.get(reverse("piggyback:subscriptions"))
        assert response.status_code == 200
        assert subscription_plan.name in response.content.decode()

    def test_demo_subscription_checkout_web(self, client, user, subscription_plan):
        client.force_login(user)
        response = client.post(
            reverse("piggyback:subscription_checkout", kwargs={"slug": subscription_plan.slug})
        )
        assert response.status_code == 302
        assert Subscription.objects.filter(user=user, plan=subscription_plan).exists()
