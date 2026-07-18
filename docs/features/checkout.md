# Checkout

Piggyback includes a full cart and checkout flow.

## Flow

1. **Cart** — `Order` with status `cart` holds items
2. **Add to cart** — via API or web UI
3. **Checkout** — applies promo codes, moves to `pending_payment`
4. **Pay** — completes payment (demo mode simulates success)
5. **Fulfil** — creates `Delivery` records and sends cards

## Pricing

Default prices (in pence):

| Item | Price |
|------|-------|
| E-Card | £2.99 |
| Posted Card | £3.99 |
| Gift Wrap | £1.99 |

Override in settings:

```python
PIGGYBACK_ECARD_PRICE = 299
PIGGYBACK_POSTED_CARD_PRICE = 399
```

## Promo codes

Built-in demo promo:

| Code | Discount |
|------|----------|
| `FIRSTCARD` | Free e-card (up to £2.99) |

## API

```bash
# Get cart
GET /api/orders/cart/

# Add to cart
POST /api/orders/add_to_cart/
{
  "card_id": 1,
  "recipient_id": 2,
  "delivery_method": "ecard"
}

# Checkout
POST /api/orders/{uuid}/checkout/
{"promo_code": "FIRSTCARD"}

# Pay (demo or Stripe)
POST /api/orders/{uuid}/pay/
{
  "success_url": "https://example.com/orders/{uuid}/",
  "cancel_url": "https://example.com/checkout/{uuid}/"
}
```

With Stripe configured, the pay endpoint returns a `checkout_url` to redirect the user. In demo mode it completes payment immediately.

See [Stripe Billing](stripe-billing.md) for full payment and subscription integration.
