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
