# Piggyback 🐷

**Design, save, and send beautiful occasion cards in Django.**

Piggyback is a Moonpig-style Django plugin that lets your users design personalised greeting cards, save them to a library, and send by email or post — with a full REST API, card editor, address book, reminders, gift add-ons, and checkout flow.

[![CI](https://github.com/kurtisrogers/piggyback/actions/workflows/ci.yml/badge.svg)](https://github.com/kurtisrogers/piggyback/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-pink.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Django 4.2+](https://img.shields.io/badge/django-4.2+-green.svg)](https://www.djangoproject.com/)

**[Landing Page](https://kurtisrogers.github.io/piggyback/)** · **[Documentation](https://kurtisrogers.github.io/piggyback/docs/)** · **[API Reference](https://kurtisrogers.github.io/piggyback/docs/api/endpoints/)**

---

## Features

| Feature | Description |
|---------|-------------|
| **Card Designer** | Fabric.js editor with text, photos, stickers, backgrounds |
| **Card Shop** | Browse templates by occasion (birthday, wedding, sympathy…) and style |
| **Card Library** | Auto-synced drafts, saved designs, sent cards, favourites |
| **E-Cards** | Instant email delivery with branded view page |
| **Posted Cards** | Pluggable postal fulfilment backend |
| **Address Book** | Recipients with email, postal address, birthdays |
| **Reminders** | Cron-ready birthday/anniversary email reminders |
| **Gift Add-ons** | Chocolates, candles, prosecco, gift wrap |
| **Checkout** | Cart, promo codes, payment hooks (Stripe-ready) |
| **REST API** | Full DRF API for headless/mobile integrations |
| **Admin** | Django admin for all models |

## Quick Start

```bash
pip install django-piggyback
```

```python
# settings.py
INSTALLED_APPS = [
    # ...
    "rest_framework",
    "django_filters",
    "piggyback",
]

# urls.py
urlpatterns = [
    path("", include("piggyback.urls")),
]
```

```bash
python manage.py migrate
python manage.py load_sample_data
python manage.py runserver
```

Visit `http://localhost:8000` — browse cards, open the editor, sign in via `/admin/login/` to save and send.

## Run the Example Project

```bash
git clone https://github.com/kurtisrogers/piggyback.git
cd piggyback
pip install -e ".[dev]"
cd example
python manage.py migrate
python manage.py load_sample_data
python manage.py createsuperuser
python manage.py runserver
```

## API Example

```bash
# Browse templates (no auth)
curl http://localhost:8000/api/templates/

# Personalise a template (authenticated)
curl -X POST http://localhost:8000/api/templates/birthday-general-classic/personalize/ \
  -b "sessionid=YOUR_SESSION"

# Add to cart and checkout
curl -X POST http://localhost:8000/api/orders/add_to_cart/ \
  -H "Content-Type: application/json" \
  -d '{"card_id": 1, "recipient_id": 1, "delivery_method": "ecard"}'
```

## Configuration

```python
PIGGYBACK_PUBLIC_URL = "https://cards.yoursite.com"
PIGGYBACK_ECARD_PRICE = 299          # pence (£2.99)
PIGGYBACK_POSTED_CARD_PRICE = 399
PIGGYBACK_REMINDER_DAYS_BEFORE = [7, 3, 1]

# Reuse existing User/profile details (no duplicate data entry)
PIGGYBACK_USER_PROFILE_RELATION = "profile"
PIGGYBACK_PROFILE_FIELD_MAP = {"phone": "phone_number", "address_line_1": "line1", ...}
```

See the [configuration docs](https://kurtisrogers.github.io/piggyback/docs/getting-started/configuration/) and [system user details guide](https://kurtisrogers.github.io/piggyback/docs/getting-started/system-user-details/).

## Project Structure

```
src/piggyback/          # Django app
├── models/             # Catalog, cards, orders, recipients, reminders
├── api/                # DRF viewsets and serializers
├── views/              # Web UI views
├── services/           # Delivery, checkout, rendering, reminders
├── templates/          # HTML templates + email templates
├── static/             # CSS + Fabric.js editor
└── management/         # load_sample_data, send_reminders

example/                # Demo Django project
docs/                   # MkDocs documentation
landing/                # GitHub Pages landing page
tests/                  # pytest suite
```

## Development

```bash
pip install -e ".[dev]"
pytest
ruff check src/ tests/
mkdocs serve -f docs/mkdocs.yml
```

## License

MIT — see [LICENSE](LICENSE).
