"""Adapters for billing identity and Stripe customer mapping."""

from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module

from django.apps import apps
from django.contrib.auth import get_user_model

from piggyback.conf import get_setting


@dataclass
class BillingIdentity:
    """Normalised billing identity for Stripe customer creation."""

    stripe_customer_id: str = ""
    email: str = ""
    name: str = ""


class BaseBillingAdapter:
    """Resolve and persist Stripe customer IDs for a user."""

    def get_billing_identity(self, user) -> BillingIdentity:
        raise NotImplementedError

    def set_stripe_customer_id(self, user, customer_id: str) -> None:
        raise NotImplementedError


class DefaultBillingAdapter(BaseBillingAdapter):
    """
    Read billing fields from the host profile, with Piggyback BillingProfile fallback.

    Configure in settings:

        PIGGYBACK_BILLING_PROFILE_RELATION = "billing"
        PIGGYBACK_BILLING_FIELD_MAP = {
            "stripe_customer_id": "stripe_customer_id",
            "email": "billing_email",
            "name": "billing_name",
        }
    """

    def get_billing_identity(self, user) -> BillingIdentity:
        identity = BillingIdentity()
        field_map: dict[str, str] = get_setting("BILLING_FIELD_MAP") or {}

        profile = self._get_host_profile(user)
        if profile is not None:
            identity = self._read_profile_fields(profile, field_map)

        if identity.stripe_customer_id:
            return self._with_user_defaults(user, identity)

        fallback = self._get_fallback_profile(user)
        if fallback is not None:
            fallback_identity = self._read_profile_fields(fallback, field_map)
            if not identity.stripe_customer_id and fallback_identity.stripe_customer_id:
                identity.stripe_customer_id = fallback_identity.stripe_customer_id
            if not identity.email and fallback_identity.email:
                identity.email = fallback_identity.email
            if not identity.name and fallback_identity.name:
                identity.name = fallback_identity.name

        return self._with_user_defaults(user, identity)

    def set_stripe_customer_id(self, user, customer_id: str) -> None:
        profile = self._get_host_profile(user)
        field_map: dict[str, str] = get_setting("BILLING_FIELD_MAP") or {}
        stripe_field = field_map.get("stripe_customer_id", "stripe_customer_id")

        if profile is not None and hasattr(profile, stripe_field):
            setattr(profile, stripe_field, customer_id)
            update_fields = [stripe_field]
            if hasattr(profile, "updated_at"):
                update_fields.append("updated_at")
            profile.save(update_fields=update_fields)
            return

        if not get_setting("USE_BILLING_PROFILE_FALLBACK"):
            return

        fallback_model = self._get_fallback_model()
        user_field = get_setting("BILLING_PROFILE_USER_FIELD") or "user"
        email_field = field_map.get("email", "billing_email")
        name_field = field_map.get("name", "billing_name")

        fallback, _ = fallback_model.objects.get_or_create(**{user_field: user})
        setattr(fallback, stripe_field, customer_id)
        if hasattr(fallback, email_field) and not getattr(fallback, email_field):
            setattr(fallback, email_field, getattr(user, "email", "") or "")
        if hasattr(fallback, name_field) and not getattr(fallback, name_field):
            name = user.get_full_name() if hasattr(user, "get_full_name") else ""
            setattr(fallback, name_field, name)
        fallback.save()

    def _get_host_profile(self, user):
        relation = get_setting("BILLING_PROFILE_RELATION")
        if not relation:
            return None
        try:
            return getattr(user, relation)
        except Exception:
            return None

    def _get_fallback_model(self):
        model_path = get_setting("BILLING_PROFILE_MODEL")
        if model_path:
            return apps.get_model(model_path)
        from piggyback.models import BillingProfile

        return BillingProfile

    def _get_fallback_profile(self, user):
        if not get_setting("USE_BILLING_PROFILE_FALLBACK"):
            return None

        fallback_model = self._get_fallback_model()

        try:
            if fallback_model._meta.label == "piggyback.BillingProfile":
                return user.piggyback_billing_profile
        except fallback_model.DoesNotExist:
            return None

        user_field = get_setting("BILLING_PROFILE_USER_FIELD") or "user"
        return fallback_model.objects.filter(**{user_field: user}).first()

    def _read_profile_fields(self, profile, field_map: dict[str, str]) -> BillingIdentity:
        identity = BillingIdentity()
        for target, source in field_map.items():
            value = getattr(profile, source, "") or ""
            if target == "stripe_customer_id":
                identity.stripe_customer_id = str(value)
            elif target == "email":
                identity.email = str(value)
            elif target == "name":
                identity.name = str(value)
        return identity

    def _with_user_defaults(self, user, identity: BillingIdentity) -> BillingIdentity:
        if not identity.email:
            identity.email = getattr(user, "email", "") or ""
        if not identity.name and hasattr(user, "get_full_name"):
            identity.name = user.get_full_name() or ""
        return identity


def get_billing_adapter() -> BaseBillingAdapter:
    adapter_path = get_setting("BILLING_ADAPTER")
    module_path, class_name = adapter_path.rsplit(".", 1)
    module = import_module(module_path)
    adapter_cls = getattr(module, class_name)
    return adapter_cls()


def get_piggyback_user_model():
    """Return configured user model or Django AUTH_USER_MODEL."""
    model_path = get_setting("USER_MODEL")
    if not model_path:
        return get_user_model()
    return apps.get_model(model_path)


def get_stripe_customer_id(user) -> str:
    return get_billing_adapter().get_billing_identity(user).stripe_customer_id


def set_stripe_customer_id(user, customer_id: str) -> None:
    get_billing_adapter().set_stripe_customer_id(user, customer_id)


def user_has_active_subscription(user) -> bool:
    from piggyback.models import Subscription

    return Subscription.objects.filter(
        user=user,
        status__in=[Subscription.Status.ACTIVE, Subscription.Status.TRIALING],
    ).exists()
