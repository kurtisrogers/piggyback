#!/usr/bin/env bash
set -euo pipefail

cd /app

export PYTHONPATH="/app/src:/app${PYTHONPATH:+:$PYTHONPATH}"

echo "Running database migrations..."
python example/manage.py migrate --noinput

if [[ "${LOAD_SAMPLE_DATA:-true}" == "true" ]]; then
  echo "Loading Piggyback sample fixtures..."
  python example/manage.py load_sample_data --fixture
fi

if [[ "${CREATE_DEMO_USER:-true}" == "true" ]]; then
  echo "Ensuring demo user exists..."
  python - <<'PY'
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "example.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
username = os.environ.get("DEMO_USERNAME", "demo")
email = os.environ.get("DEMO_EMAIL", "demo@piggyback.example")
password = os.environ.get("DEMO_PASSWORD", "demo12345")

user, created = User.objects.get_or_create(
    username=username,
    defaults={
        "email": email,
        "first_name": "Demo",
        "last_name": "User",
        "is_staff": True,
        "is_superuser": True,
    },
)
user.set_password(password)
user.is_staff = True
user.is_superuser = True
user.save()
print("Demo user created." if created else "Demo user updated.")
PY
fi

echo "Starting: $*"
exec "$@"
