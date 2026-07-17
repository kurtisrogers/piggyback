# Installation

## Requirements

- Python 3.10+
- Django 4.2+
- Pillow (for card preview rendering)

## Install from source

```bash
git clone https://github.com/kurtisrogers/piggyback.git
cd piggyback
pip install -e ".[dev]"
```

## Django setup

Add to your `settings.py`:

```python
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "django_filters",
    "piggyback",
]

# Optional Piggyback settings
PIGGYBACK_PUBLIC_URL = "https://cards.yoursite.com"
PIGGYBACK_ECARD_PRICE = 299          # pence
PIGGYBACK_POSTED_CARD_PRICE = 399
PIGGYBACK_REMINDER_DAYS_BEFORE = [7, 3, 1]
```

Wire up URLs:

```python
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("piggyback.urls")),
]
```

Run migrations and load sample data:

```bash
python manage.py migrate
python manage.py load_sample_data
python manage.py createsuperuser
python manage.py runserver
```

## Media files

Piggyback uses `ImageField` for templates, previews, and uploads. Configure media in development:

```python
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"
```

## Email delivery

For e-cards, configure Django's email backend:

```python
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.example.com"
# ...
```

In development, use the console backend to see emails in your terminal:

```python
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
```
