import os

import pytest
from django.core.management import call_command

# Playwright drives sync Django ORM from its worker thread during steps.
os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")


@pytest.fixture
def loaded_catalog(db):
    call_command("load_sample_data", fixture=True)
