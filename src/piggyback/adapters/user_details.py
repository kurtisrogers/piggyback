"""Adapters for reading sender/recipient details from the host project's User model."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from importlib import import_module
from typing import Any

from piggyback.conf import get_setting


@dataclass
class UserDetails:
    """Normalised user details used across Piggyback."""

    first_name: str = ""
    last_name: str = ""
    email: str = ""
    phone: str = ""
    address_line_1: str = ""
    address_line_2: str = ""
    city: str = ""
    county: str = ""
    postcode: str = ""
    country: str = "GB"
    birthday: Any = None
    anniversary: Any = None

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def as_recipient_defaults(self) -> dict[str, Any]:
        data = asdict(self)
        for date_field in ("birthday", "anniversary"):
            if not data.get(date_field):
                data[date_field] = None
        return data


class BaseUserDetailsAdapter:
    """Resolve user details from the host project's auth models."""

    def get_user_details(self, user) -> UserDetails:
        raise NotImplementedError

    def get_display_name(self, user) -> str:
        details = self.get_user_details(user)
        if details.full_name:
            return details.full_name
        return user.get_full_name() or getattr(user, "username", str(user))


class DefaultUserDetailsAdapter(BaseUserDetailsAdapter):
    """
    Read user details from AUTH_USER_MODEL and an optional related profile.

    Configure field mapping in Django settings:

        PIGGYBACK_USER_PROFILE_RELATION = "profile"
        PIGGYBACK_USER_FIELD_MAP = {
            "email": "email",
            "first_name": "first_name",
            "last_name": "last_name",
        }
        PIGGYBACK_PROFILE_FIELD_MAP = {
            "phone": "phone_number",
            "address_line_1": "line1",
            "city": "city",
            "postcode": "postcode",
        }
    """

    def get_user_details(self, user) -> UserDetails:
        if user is None or not getattr(user, "is_authenticated", False):
            return UserDetails()

        details = UserDetails()
        user_map: dict[str, str] = get_setting("USER_FIELD_MAP") or {}
        profile_map: dict[str, str] = get_setting("PROFILE_FIELD_MAP") or {}

        for target_field, source_field in user_map.items():
            if hasattr(details, target_field):
                setattr(details, target_field, _coerce_value(getattr(user, source_field, "")))

        profile = self._get_profile(user)
        if profile is not None:
            for target_field, source_field in profile_map.items():
                if hasattr(details, target_field):
                    value = getattr(profile, source_field, "")
                    setattr(details, target_field, _coerce_value(value))

        if not details.email:
            details.email = getattr(user, "email", "") or ""
        if not details.first_name:
            details.first_name = getattr(user, "first_name", "") or ""
        if not details.last_name:
            details.last_name = getattr(user, "last_name", "") or ""

        return details

    def _get_profile(self, user):
        relation = get_setting("USER_PROFILE_RELATION")
        if not relation:
            return None
        try:
            return getattr(user, relation)
        except Exception:
            return None


def _coerce_value(value: Any) -> Any:
    if value is None:
        return ""
    return value


def get_user_details_adapter() -> BaseUserDetailsAdapter:
    adapter_path = get_setting("USER_DETAILS_ADAPTER")
    module_path, class_name = adapter_path.rsplit(".", 1)
    module = import_module(module_path)
    adapter_cls = getattr(module, class_name)
    return adapter_cls()


def get_user_details(user) -> UserDetails:
    if user is None or not getattr(user, "is_authenticated", False):
        return UserDetails()

    if not get_setting("USE_SYSTEM_USER_DETAILS"):
        return UserDetails(
            first_name=getattr(user, "first_name", "") or "",
            last_name=getattr(user, "last_name", "") or "",
            email=getattr(user, "email", "") or "",
        )
    return get_user_details_adapter().get_user_details(user)


def get_user_display_name(user) -> str:
    if not get_setting("USE_SYSTEM_USER_DETAILS"):
        return user.get_full_name() or getattr(user, "username", str(user))
    return get_user_details_adapter().get_display_name(user)


def sync_user_recipient(user):
    """
    Create or update the owner's address-book entry from system user details.

    Returns the synced Recipient, or None when sync is disabled.
    """
    from piggyback.models import Recipient

    if not get_setting("AUTO_SYNC_USER_RECIPIENT"):
        return None

    details = get_user_details(user)
    if not any([details.email, details.full_name, details.address_line_1]):
        return None

    recipient, _ = Recipient.objects.update_or_create(
        owner=user,
        is_system_user=True,
        defaults=details.as_recipient_defaults(),
    )
    return recipient
