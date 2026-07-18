"""Django settings for Piggyback example project."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY", "django-insecure-piggyback-demo-only-change-in-production"
)

DEBUG = os.environ.get("DJANGO_DEBUG", "true").lower() in {"1", "true", "yes"}

ALLOWED_HOSTS = [
    host.strip() for host in os.environ.get("DJANGO_ALLOWED_HOSTS", "*").split(",") if host.strip()
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "django_filters",
    "example.accounts",
    "piggyback",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "example.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "example.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.environ.get("DATABASE_PATH", str(BASE_DIR / "db.sqlite3")),
    }
}

if os.environ.get("POSTGRES_HOST"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("POSTGRES_DB", "piggyback"),
            "USER": os.environ.get("POSTGRES_USER", "piggyback"),
            "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "piggyback"),
            "HOST": os.environ["POSTGRES_HOST"],
            "PORT": os.environ.get("POSTGRES_PORT", "5432"),
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
]

LANGUAGE_CODE = "en-gb"
TIME_ZONE = "Europe/London"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 24,
}

LOGIN_URL = "/admin/login/"
LOGIN_REDIRECT_URL = "/"

PIGGYBACK_PUBLIC_URL = os.environ.get("PIGGYBACK_PUBLIC_URL", "http://localhost:8000")

# Stripe (optional — leave unset for demo payments)
PIGGYBACK_STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")
PIGGYBACK_STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY")
PIGGYBACK_STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")
PIGGYBACK_DEMO_PAYMENTS = not bool(PIGGYBACK_STRIPE_SECRET_KEY)
PIGGYBACK_STRIPE_ORDER_SUCCESS_URL = f"{PIGGYBACK_PUBLIC_URL}/orders/{{uuid}}/"
PIGGYBACK_STRIPE_ORDER_CANCEL_URL = f"{PIGGYBACK_PUBLIC_URL}/checkout/{{uuid}}/"
PIGGYBACK_STRIPE_SUBSCRIPTION_SUCCESS_URL = f"{PIGGYBACK_PUBLIC_URL}/subscriptions/"
PIGGYBACK_STRIPE_SUBSCRIPTION_CANCEL_URL = f"{PIGGYBACK_PUBLIC_URL}/subscriptions/"
PIGGYBACK_STRIPE_BILLING_PORTAL_RETURN_URL = f"{PIGGYBACK_PUBLIC_URL}/subscriptions/"

# Piggyback reads sender/recipient details from User + profile
PIGGYBACK_USER_PROFILE_RELATION = "profile"
PIGGYBACK_PROFILE_FIELD_MAP = {
    "phone": "phone_number",
    "address_line_1": "line1",
    "address_line_2": "line2",
    "city": "city",
    "county": "county",
    "postcode": "postcode",
    "country": "country",
    "birthday": "birthday",
}
