# Configuration

All Piggyback settings use the `PIGGYBACK_` prefix in Django settings.

| Setting | Default | Description |
|---------|---------|-------------|
| `PIGGYBACK_CARD_WIDTH` | `1748` | Card canvas width (px at 300 DPI) |
| `PIGGYBACK_CARD_HEIGHT` | `2480` | Card canvas height (px at 300 DPI) |
| `PIGGYBACK_ECARD_PRICE` | `299` | E-card price in pence |
| `PIGGYBACK_POSTED_CARD_PRICE` | `399` | Posted card price in pence |
| `PIGGYBACK_GIFT_WRAP_PRICE` | `199` | Gift wrap add-on in pence |
| `PIGGYBACK_DEFAULT_FROM_EMAIL` | `None` | Sender email for e-cards |
| `PIGGYBACK_PUBLIC_URL` | — | Base URL for e-card view links |
| `PIGGYBACK_ALLOW_USER_UPLOADS` | `True` | Allow photo uploads in editor |
| `PIGGYBACK_MAX_UPLOAD_SIZE_MB` | `10` | Max upload size |
| `PIGGYBACK_LIBRARY_AUTO_SAVE_DRAFTS` | `True` | Auto-add drafts to library |
| `PIGGYBACK_MAX_SAVED_CARDS_PER_USER` | `500` | Library size limit |
| `PIGGYBACK_REMINDER_DAYS_BEFORE` | `[7, 3, 1]` | Reminder schedule |
| `PIGGYBACK_ECARD_DELIVERY_BACKEND` | Email backend path | E-card delivery class |
| `PIGGYBACK_POSTAL_DELIVERY_BACKEND` | Postal backend path | Postal fulfilment class |
| `PIGGYBACK_USE_SYSTEM_USER_DETAILS` | `True` | Read user details from host User/profile |
| `PIGGYBACK_AUTO_SYNC_USER_RECIPIENT` | `True` | Sync address-book entry from system user |
| `PIGGYBACK_USER_PROFILE_RELATION` | `None` | Profile relation on User, e.g. `"profile"` |
| `PIGGYBACK_USER_FIELD_MAP` | see defaults | Map User fields to Piggyback details |
| `PIGGYBACK_PROFILE_FIELD_MAP` | `{}` | Map profile fields to Piggyback details |
| `PIGGYBACK_STRIPE_SECRET_KEY` | `None` | Stripe secret key |
| `PIGGYBACK_STRIPE_PUBLISHABLE_KEY` | `None` | Stripe publishable key |
| `PIGGYBACK_STRIPE_WEBHOOK_SECRET` | `None` | Stripe webhook signing secret |
| `PIGGYBACK_DEMO_PAYMENTS` | `True` | Simulate payments when Stripe is unset |
| `PIGGYBACK_SUBSCRIPTION_ENABLED` | `True` | Enable subscription sign-ups |
| `PIGGYBACK_BILLING_ADAPTER` | Default adapter | Billing identity adapter class |
| `PIGGYBACK_BILLING_PROFILE_RELATION` | `None` | Host billing profile relation on User |
| `PIGGYBACK_BILLING_FIELD_MAP` | see defaults | Map billing profile fields |
| `PIGGYBACK_BILLING_PROFILE_MODEL` | `None` | Custom fallback billing model |
| `PIGGYBACK_BILLING_PROFILE_USER_FIELD` | `"user"` | User FK on fallback billing model |
| `PIGGYBACK_USE_BILLING_PROFILE_FALLBACK` | `True` | Use Piggyback billing profile fallback |
| `PIGGYBACK_USER_MODEL` | `None` | Optional user model override |

See [System User Details](system-user-details.md) for full integration guide.

See [Stripe Billing](../features/stripe-billing.md) for payment and subscription setup.

## Custom delivery backends

Implement `piggyback.services.delivery.DeliveryBackend`:

```python
from piggyback.services.delivery import DeliveryBackend

class MyPrintPartnerBackend(DeliveryBackend):
    def send(self, delivery) -> bool:
        # Submit to your print partner API
        ...
        return True
```

Then in settings:

```python
PIGGYBACK_POSTAL_DELIVERY_BACKEND = "myapp.backends.MyPrintPartnerBackend"
```
