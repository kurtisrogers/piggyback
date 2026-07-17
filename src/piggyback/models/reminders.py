from django.conf import settings
from django.db import models

from piggyback.models.base import TimeStampedModel
from piggyback.models.catalog import Occasion
from piggyback.models.recipients import Recipient


class Reminder(TimeStampedModel):
    """Occasion reminders — birthdays, anniversaries, custom dates."""

    class ReminderType(models.TextChoices):
        BIRTHDAY = "birthday", "Birthday"
        ANNIVERSARY = "anniversary", "Anniversary"
        CUSTOM = "custom", "Custom Occasion"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="piggyback_reminders",
    )
    recipient = models.ForeignKey(
        Recipient,
        on_delete=models.CASCADE,
        related_name="reminders",
        null=True,
        blank=True,
    )
    occasion = models.ForeignKey(
        Occasion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reminders",
    )
    reminder_type = models.CharField(max_length=20, choices=ReminderType.choices)
    title = models.CharField(max_length=200)
    event_date = models.DateField()
    days_before = models.PositiveSmallIntegerField(default=7)
    is_active = models.BooleanField(default=True)
    last_sent_year = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["event_date"]

    def __str__(self):
        return f"{self.title} — {self.event_date}"
