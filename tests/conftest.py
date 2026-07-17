import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command

User = get_user_model()

DEMO_USERNAME = "demo"
DEMO_PASSWORD = "demo12345"


@pytest.fixture
def demo_user(db):
    user, _ = User.objects.get_or_create(
        username=DEMO_USERNAME,
        defaults={
            "email": "demo@piggyback.example",
            "first_name": "Demo",
            "last_name": "User",
            "is_staff": True,
            "is_superuser": True,
        },
    )
    user.set_password(DEMO_PASSWORD)
    user.save()
    return user


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="alice",
        email="alice@example.com",
        password="pass12345",
        first_name="Alice",
        last_name="Anderson",
    )


@pytest.fixture
def api_client(user):
    from rest_framework.test import APIClient

    client = APIClient()
    client.force_authenticate(user=user)
    return client
