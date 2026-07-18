from django.conf import settings
from django.db import models
from django.utils import timezone

from piggyback.models.base import TimeStampedModel


class BillingProfile(TimeStampedModel):
    """
    Piggyback-owned billing profile used when the host app has no billing model.

    Override via PIGGYBACK_BILLING_PROFILE_MODEL or map fields on your own profile
    with PIGGYBACK_BILLING_PROFILE_RELATION / PIGGYBACK_BILLING_FIELD_MAP.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="piggyback_billing_profile",
    )
    stripe_customer_id = models.CharField(max_length=255, blank=True)
    billing_email = models.EmailField(blank=True)
    billing_name = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = "billing profile"
        verbose_name_plural = "billing profiles"

    def __str__(self):
        return f"Billing for {self.user}"


class SubscriptionPlan(TimeStampedModel):
    """Subscription tier synced with a Stripe Price."""

    class Interval(models.TextChoices):
        MONTH = "month", "Monthly"
        YEAR = "year", "Yearly"

    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    stripe_price_id = models.CharField(max_length=255, blank=True)
    amount_pence = models.PositiveIntegerField(default=0)
    currency = models.CharField(max_length=3, default="GBP")
    interval = models.CharField(
        max_length=10,
        choices=Interval.choices,
        default=Interval.MONTH,
    )
    is_active = models.BooleanField(default=True)
    grants_premium_access = models.BooleanField(
        default=True,
        help_text="Subscribers can access premium templates and assets.",
    )

    class Meta:
        ordering = ["amount_pence"]

    def __str__(self):
        return self.name


class Subscription(TimeStampedModel):
    """A user's active or historical Stripe subscription."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        TRIALING = "trialing", "Trialing"
        PAST_DUE = "past_due", "Past due"
        CANCELED = "canceled", "Canceled"
        INCOMPLETE = "incomplete", "Incomplete"
        UNPAID = "unpaid", "Unpaid"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="piggyback_subscriptions",
    )
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.PROTECT,
        related_name="subscriptions",
    )
    stripe_subscription_id = models.CharField(max_length=255, unique=True)
    stripe_customer_id = models.CharField(max_length=255, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.INCOMPLETE,
    )
    current_period_start = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)
    cancel_at_period_end = models.BooleanField(default=False)
    canceled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} — {self.plan.name} ({self.status})"

    @property
    def is_active(self) -> bool:
        return self.status in {
            self.Status.ACTIVE,
            self.Status.TRIALING,
        } and (
            self.current_period_end is None or self.current_period_end >= timezone.now()
        )
