# Piggyback Documentation

**Piggyback** is a Django plugin for designing, saving, and sending occasion cards — think Moonpig, but as a drop-in Django app with a full REST API.

[![PyPI](https://img.shields.io/pypi/v/pypiggyback.svg)](https://pypi.org/project/pypiggyback/)
[![Python 3.10+](https://img.shields.io/pypi/pyversions/pypiggyback.svg)](https://pypi.org/project/pypiggyback/)

## What you get

- **Card Designer** — Fabric.js-powered drag-and-drop editor with text, photos, stickers, and backgrounds
- **Card Shop** — Browse templates by occasion and style
- **Card Library** — Auto-synced library of drafts, saved designs, and sent cards
- **Recipients** — Full address book with birthday/anniversary tracking
- **Delivery** — E-cards via email, posted cards (with fulfilment stub), print-at-home
- **Gift Add-ons** — Attach chocolates, candles, and more to posted orders
- **Reminders** — Email reminders before important dates
- **Checkout** — Cart, promo codes, and payment flow (demo mode included)
- **REST API** — Full DRF API for headless/mobile integrations
- **Admin** — Django admin for templates, orders, deliveries, and more

## Quick install

Install from [PyPI](https://pypi.org/project/pypiggyback/):

```bash
pip install pypiggyback
```

```python
# settings.py
INSTALLED_APPS = [
    # ...
    "rest_framework",
    "django_filters",
    "piggyback",
]

urlpatterns = [
    path("", include("piggyback.urls")),
]
```

```bash
python manage.py migrate
python manage.py load_sample_data
python manage.py runserver
```

Visit `http://localhost:8000` and start designing cards.

!!! note "Package vs app name"
    Install with `pip install pypiggyback`, then add `"piggyback"` to `INSTALLED_APPS`.

## Links

- [PyPI Project](https://pypi.org/project/pypiggyback/)
- [Quick Start](getting-started/quickstart.md)
- [Installation Guide](getting-started/installation.md)
- [API Reference](api/endpoints.md)
- [Architecture](development/architecture.md)
- [GitHub Repository](https://github.com/kurtisrogers/piggyback)
