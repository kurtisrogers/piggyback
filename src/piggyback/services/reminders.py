"""Occasion reminder processing."""

from datetime import date

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core.mail import send_mail

from piggyback.models import Reminder


def upcoming_reminders(for_date: date | None = None) -> list[Reminder]:
    """Return reminders that should fire on the given date."""
    today = for_date or date.today()
    due = []
    for reminder in Reminder.objects.filter(is_active=True).select_related("user", "recipient"):
        target = reminder.event_date - relativedelta(days=reminder.days_before)
        if target.month == today.month and target.day == today.day:
            if reminder.last_sent_year != today.year:
                due.append(reminder)
    return due


def send_reminder_email(reminder: Reminder) -> bool:
    user = reminder.user
    if not user.email:
        return False

    subject = f"Reminder: {reminder.title} is coming up!"
    body = (
        f"Hi {user.get_full_name() or user.username},\n\n"
        f"This is a friendly reminder that {reminder.title} "
        f"is on {reminder.event_date.strftime('%d %B')}.\n\n"
        f"Send a card now: {getattr(settings, 'PIGGYBACK_PUBLIC_URL', '/')}/catalog/\n"
    )
    send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [user.email])
    reminder.last_sent_year = date.today().year
    reminder.save(update_fields=["last_sent_year", "updated_at"])
    return True


def process_reminders(for_date: date | None = None) -> int:
    sent = 0
    for reminder in upcoming_reminders(for_date):
        if send_reminder_email(reminder):
            sent += 1
    return sent
