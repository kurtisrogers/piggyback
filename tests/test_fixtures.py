import pytest
from django.core.management import call_command

from piggyback.models import CardTemplate, GiftAddon, OccasionCategory


@pytest.mark.django_db
def test_sample_fixture_loads_catalog():
    call_command("load_sample_data", fixture=True)
    assert OccasionCategory.objects.count() >= 8
    assert CardTemplate.objects.filter(is_active=True).count() >= 12
    assert GiftAddon.objects.filter(is_active=True).count() >= 3


@pytest.mark.django_db
def test_load_sample_data_command():
    call_command("load_sample_data")
    assert OccasionCategory.objects.filter(slug="birthday").exists()
