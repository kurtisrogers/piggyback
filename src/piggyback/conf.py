from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from piggyback.defaults import *  # noqa: F403


def get_setting(name: str):
    """Return a Piggyback setting, falling back to defaults."""
    return getattr(settings, f"PIGGYBACK_{name}", globals().get(name))


def require_setting(name: str):
    value = get_setting(name)
    if value is None:
        raise ImproperlyConfigured(f"PIGGYBACK_{name} must be set in Django settings.")
    return value
