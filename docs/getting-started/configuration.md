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
