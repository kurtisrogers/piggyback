from django.core.management.base import BaseCommand

from piggyback.services.reminders import process_reminders


class Command(BaseCommand):
    help = "Send occasion reminder emails for upcoming events."

    def handle(self, *args, **options):
        sent = process_reminders()
        self.stdout.write(self.style.SUCCESS(f"Sent {sent} reminder(s)."))
