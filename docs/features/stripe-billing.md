# Stripe Billing

Piggyback supports one-time card order payments and monthly subscriptions via Stripe, with a demo mode when Stripe is not configured.

## Install

```bash
pip install pypiggyback[stripe]
```

## Quick setup

```python
# settings.py
PIGGYBACK_STRIPE_SECRET_KEY = os.environ["STRIPE_SECRET_KEY"]
PIGGYBACK_STRIPE_PUBLISHABLE_KEY = os.environ["STRIPE_PUBLISHABLE_KEY"]
PIGGYBACK_STRIPE_WEBHOOK_SECRET = os.environ["STRIPE_WEBHOOK_SECRET"]
PIGGYBACK_DEMO_PAYMENTS = False

PIGGYBACK_STRIPE_ORDER_SUCCESS_URL = "https://example.com/orders/{uuid}/"
PIGGYBACK_STRIPE_ORDER_CANCEL_URL = "https://example.com/checkout/{uuid}/"
PIGGYBACK_STRIPE_SUBSCRIPTION_SUCCESS_URL = "https://example.com/subscriptions/"
PIGGYBACK_STRIPE_SUBSCRIPTION_CANCEL_URL = "https://example.com/subscriptions/"
PIGGYBACK_STRIPE_BILLING_PORTAL_RETURN_URL = "https://example.com/subscriptions/"
```

Register the webhook endpoint in your Stripe dashboard:

```
POST /stripe/webhook/
```

Listen for:

- `checkout.session.completed`
- `customer.subscription.updated`
- `customer.subscription.deleted`

## Subscription plans

Create `SubscriptionPlan` records in Django admin (or via fixtures) and set each plan's `stripe_price_id` to a Stripe Price ID.

## One-time payments

1. User checks out — order moves to `pending_payment`
2. Call `POST /api/orders/{uuid}/pay/` with `success_url` and `cancel_url`
3. Redirect the user to the returned `checkout_url`
4. Stripe webhook calls `complete_payment(order)` on success

## Subscriptions

- List plans: `GET /api/subscriptions/plans/`
- Start checkout: `POST /api/subscriptions/checkout/` with `plan_slug`
- Manage billing: `POST /api/subscriptions/portal/` with `return_url`
- Check status: `GET /api/me/subscription/`

Web UI is available at `/subscriptions/`.

## Demo mode

When `PIGGYBACK_STRIPE_SECRET_KEY` is unset and `PIGGYBACK_DEMO_PAYMENTS=True` (default), payments and subscriptions are simulated without Stripe.

## Billing profile integration

Piggyback stores Stripe customer IDs on a billing profile. You can use your own model or Piggyback's fallback.

### Host billing profile

Map your existing profile:

```python
PIGGYBACK_BILLING_PROFILE_RELATION = "billing"
PIGGYBACK_BILLING_FIELD_MAP = {
    "stripe_customer_id": "stripe_customer_id",
    "email": "billing_email",
    "name": "billing_name",
}
```

### Piggyback fallback

If no host profile is configured, Piggyback creates a `BillingProfile` per user automatically.

### Custom fallback model

Replace the fallback model entirely:

```python
PIGGYBACK_BILLING_PROFILE_MODEL = "myapp.CustomerBilling"
PIGGYBACK_BILLING_PROFILE_USER_FIELD = "user"
PIGGYBACK_BILLING_FIELD_MAP = {
    "stripe_customer_id": "stripe_id",
    "email": "email",
    "name": "full_name",
}
```

### User model override

If you need Piggyback helpers to resolve a specific user model:

```python
PIGGYBACK_USER_MODEL = "myapp.User"
```

This must be compatible with `AUTH_USER_MODEL`.

## Premium access

Use `user_has_active_subscription(user)` from `piggyback.adapters` to gate premium templates and assets.
