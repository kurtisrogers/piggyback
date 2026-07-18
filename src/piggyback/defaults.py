"""Default configuration for Piggyback."""

# Card dimensions (pixels at 300 DPI — standard greeting card)
CARD_WIDTH = 1748
CARD_HEIGHT = 2480

# Pricing (pence/cents) — override in host project
ECARD_PRICE = 299
POSTED_CARD_PRICE = 399
GIFT_WRAP_PRICE = 199

# Delivery
DEFAULT_FROM_EMAIL = None  # falls back to Django DEFAULT_FROM_EMAIL
ECARD_DELIVERY_BACKEND = "piggyback.services.delivery.EmailDeliveryBackend"
POSTAL_DELIVERY_BACKEND = "piggyback.services.delivery.PostalDeliveryBackend"

# Media
ALLOW_USER_UPLOADS = True
MAX_UPLOAD_SIZE_MB = 10

# Library
LIBRARY_AUTO_SAVE_DRAFTS = True
MAX_SAVED_CARDS_PER_USER = 500

# Reminders
REMINDER_DAYS_BEFORE = [7, 3, 1]

# Editor
EDITOR_CANVAS_LIBRARY = "fabric"

# System user integration — read details from the host project's User/profile
USE_SYSTEM_USER_DETAILS = True
AUTO_SYNC_USER_RECIPIENT = True
USER_DETAILS_ADAPTER = "piggyback.adapters.user_details.DefaultUserDetailsAdapter"
USER_PROFILE_RELATION = None  # e.g. "profile" for user.profile
USER_FIELD_MAP = {
    "email": "email",
    "first_name": "first_name",
    "last_name": "last_name",
}
PROFILE_FIELD_MAP = {}

# Billing / Stripe
PAYMENT_BACKEND = "piggyback.services.payments.stripe.StripePaymentBackend"
STRIPE_SECRET_KEY = None
STRIPE_PUBLISHABLE_KEY = None
STRIPE_WEBHOOK_SECRET = None
DEMO_PAYMENTS = True
SUBSCRIPTION_ENABLED = True

# Billing profile — host app integration with Piggyback fallback
BILLING_ADAPTER = "piggyback.adapters.billing.DefaultBillingAdapter"
BILLING_PROFILE_RELATION = None
BILLING_FIELD_MAP = {
    "stripe_customer_id": "stripe_customer_id",
    "email": "billing_email",
    "name": "billing_name",
}
USE_BILLING_PROFILE_FALLBACK = True
BILLING_PROFILE_MODEL = None  # e.g. "myapp.BillingInfo" — replaces BillingProfile fallback
BILLING_PROFILE_USER_FIELD = "user"  # FK field on fallback billing model

# Optional user model override (must be compatible with AUTH_USER_MODEL)
USER_MODEL = None

STRIPE_ORDER_SUCCESS_URL = None
STRIPE_ORDER_CANCEL_URL = None
STRIPE_SUBSCRIPTION_SUCCESS_URL = None
STRIPE_SUBSCRIPTION_CANCEL_URL = None
STRIPE_BILLING_PORTAL_RETURN_URL = None
