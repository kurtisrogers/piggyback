# Quick Start

Get Piggyback running in under five minutes.

## 1. Install from PyPI

```bash
pip install pypiggyback
```

Published at [pypi.org/project/pypiggyback](https://pypi.org/project/pypiggyback/). The pip package is `pypiggyback`; the Django app is `piggyback`.

Add to your Django project:

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
  path("admin/", admin.site.urls),
  path("", include("piggyback.urls")),
]
```

Then migrate and load sample card templates:

```bash
python manage.py migrate
python manage.py load_sample_data
python manage.py createsuperuser
python manage.py runserver
```

!!! tip "No Django project yet?"
    Clone the example app instead — see [Run the example project](#run-the-example-project) below.

## 2. Browse the card shop

Open [http://localhost:8000/catalog/](http://localhost:8000/catalog/) to browse templates by occasion and style.

## 3. Design a card

Click any template to open the card editor. You can:

- Add and edit text (double-click)
- Upload photos
- Add emoji stickers
- Change background colours
- Write an inside message

Sign in via `/admin/login/` to save your design.

## 4. Send a card

1. Save your design in the editor
2. Add a recipient via the web UI, API, or admin
3. Add to cart and checkout
4. Use promo code `FIRSTCARD` for a free e-card

## 5. Explore the API

```bash
# List templates
curl http://localhost:8000/api/templates/

# Personalise a template (authenticated)
curl -X POST http://localhost:8000/api/templates/birthday-general-classic/personalize/ \
  -H "Cookie: sessionid=YOUR_SESSION"
```

## 6. Set up reminders

```bash
# Add to crontab — runs daily
0 9 * * * cd /path/to/project && python manage.py send_reminders
```

## Run the example project

To try Piggyback without wiring it into your own Django app:

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

Or use Docker:

```bash
docker compose up --build
```

Demo login: `demo` / `demo12345` — see [Docker](docker.md).

## Next steps

- [Installation](installation.md) — PyPI extras, media, email
- [Configuration](configuration.md) — pricing, delivery, settings
- [System User Details](system-user-details.md) — reuse your app's user profile
- [API Reference](../api/endpoints.md)
