# Delivery

Piggyback supports three delivery methods:

| Method | Code | Description |
|--------|------|-------------|
| E-Card | `ecard` | Instant email delivery with view link |
| Posted | `post` | Physical card printed and posted |
| Print at Home | `print` | PDF/download for self-printing |

## E-Card delivery

E-cards are sent via Django's email framework. Recipients receive a branded email with a link to view their card at `/cards/view/{token}/`.

Configure the public URL for view links:

```python
PIGGYBACK_PUBLIC_URL = "https://cards.yoursite.com"
```

## Postal delivery

The built-in `PostalDeliveryBackend` is a stub that queues cards for fulfilment and generates a tracking reference (`PB-00000001`). Replace it with your print partner integration:

```python
PIGGYBACK_POSTAL_DELIVERY_BACKEND = "myapp.backends.PrintPartnerBackend"
```

## Scheduled delivery

Schedule a card for future delivery:

```bash
POST /api/orders/add_to_cart/
{
  "card_id": 1,
  "recipient_id": 2,
  "delivery_method": "ecard",
  "scheduled_for": "2026-12-25T09:00:00Z"
}
```

## Gift add-ons

Attach gifts to posted cards:

```bash
POST /api/orders/add_to_cart/
{
  "card_id": 1,
  "recipient_id": 2,
  "delivery_method": "post",
  "gift_addon_id": 1,
  "gift_wrap": true
}
```

## Tracking

```bash
GET /api/deliveries/
```

Returns delivery status, tracking reference, and view token for each delivery.
