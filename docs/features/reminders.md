# Reminders

Never miss a birthday or anniversary with Piggyback's reminder system.

## How it works

1. Create a `Reminder` linked to a recipient and/or occasion
2. Set the event date and how many days before to notify
3. Run `python manage.py send_reminders` daily (via cron)
4. Users receive an email prompting them to send a card

## API

```bash
POST /api/reminders/
{
  "recipient": 1,
  "reminder_type": "birthday",
  "title": "Bob's Birthday",
  "event_date": "2026-08-15",
  "days_before": 7
}
```

## Management command

```bash
# Send due reminders for today
python manage.py send_reminders
```

Add to crontab:

```cron
0 9 * * * cd /path/to/project && /path/to/venv/bin/python manage.py send_reminders
```

## Configuration

```python
PIGGYBACK_REMINDER_DAYS_BEFORE = [7, 3, 1]  # default schedule
```

## Recipient birthdays

Recipients can store `birthday` and `anniversary` dates. Create reminders linked to recipients for automatic occasion tracking.
