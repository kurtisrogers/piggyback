from django.db.models.signals import post_save
from django.dispatch import receiver

from piggyback.conf import get_setting
from piggyback.models import Card, CardLibraryEntry, CardStatus


@receiver(post_save, sender=Card)
def sync_card_library(sender, instance: Card, created, **kwargs):
    """Keep the user's card library in sync with card status changes."""
    if not get_setting("LIBRARY_AUTO_SAVE_DRAFTS") and instance.status == CardStatus.DRAFT:
        return

    entry_type_map = {
        CardStatus.DRAFT: CardLibraryEntry.EntryType.DRAFT,
        CardStatus.SAVED: CardLibraryEntry.EntryType.SAVED,
        CardStatus.SENT: CardLibraryEntry.EntryType.SENT,
        CardStatus.DELIVERED: CardLibraryEntry.EntryType.SENT,
        CardStatus.ORDERED: CardLibraryEntry.EntryType.SAVED,
    }
    entry_type = entry_type_map.get(instance.status)
    if not entry_type:
        return

    CardLibraryEntry.objects.update_or_create(
        user=instance.owner,
        card=instance,
        entry_type=entry_type,
        defaults={},
    )
