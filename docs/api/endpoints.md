# API Endpoints

## Catalog

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/categories/` | No | List occasion categories |
| GET | `/api/categories/{slug}/` | No | Category detail |
| GET | `/api/occasions/` | No | List occasions |
| GET | `/api/occasions/{slug}/` | No | Occasion detail |
| GET | `/api/templates/` | No | List card templates |
| GET | `/api/templates/{slug}/` | No | Template detail |
| POST | `/api/templates/{slug}/personalize/` | Yes | Create card from template |
| GET | `/api/assets/` | No | List design assets |
| GET | `/api/gifts/` | No | List gift add-ons |

## Cards

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/cards/` | Yes | List user's cards |
| POST | `/api/cards/` | Yes | Create a card |
| GET | `/api/cards/{id}/` | Yes | Card detail |
| PUT | `/api/cards/{id}/` | Yes | Update card |
| DELETE | `/api/cards/{id}/` | Yes | Delete card |
| POST | `/api/cards/{id}/save_design/` | Yes | Save canvas + message |
| POST | `/api/cards/{id}/favorite/` | Yes | Toggle favourite |

## Library

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/library/` | Yes | List library entries |
| GET | `/api/library/?type=sent` | Yes | Filter by type |

| GET | `/api/me/details/` | Yes | Resolved system user details |
| POST | `/api/me/sync_recipient/` | Yes | Sync system user to address book |

## Recipients

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/recipients/` | Yes | List recipients |
| POST | `/api/recipients/` | Yes | Create recipient |
| GET | `/api/recipients/{id}/` | Yes | Recipient detail |
| PUT | `/api/recipients/{id}/` | Yes | Update recipient |
| DELETE | `/api/recipients/{id}/` | Yes | Delete recipient |

## Orders

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/orders/` | Yes | List orders |
| GET | `/api/orders/cart/` | Yes | Current cart |
| POST | `/api/orders/add_to_cart/` | Yes | Add card to cart |
| POST | `/api/orders/{uuid}/checkout/` | Yes | Proceed to checkout |
| POST | `/api/orders/{uuid}/pay/` | Yes | Complete payment |

## Deliveries

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/deliveries/` | Yes | List deliveries |

## Reminders

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/reminders/` | Yes | List reminders |
| POST | `/api/reminders/` | Yes | Create reminder |
| PUT | `/api/reminders/{id}/` | Yes | Update reminder |
| DELETE | `/api/reminders/{id}/` | Yes | Delete reminder |

## Public e-card view

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/cards/view/{token}/` | No | View received e-card |
