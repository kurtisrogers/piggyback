from django.conf import settings
from django.db import models
from django.utils import timezone

from piggyback.models.base import TimeStampedModel
from piggyback.models.catalog import CardTemplate, Occasion


class CardStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    SAVED = "saved", "Saved"
    ORDERED = "ordered", "Ordered"
    SENT = "sent", "Sent"
    DELIVERED = "delivered", "Delivered"
    ARCHIVED = "archived", "Archived"


class Card(TimeStampedModel):
    """A user's personalised card design."""

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="piggyback_cards",
    )
    template = models.ForeignKey(
        CardTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cards",
    )
    occasion = models.ForeignKey(
        Occasion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cards",
    )
    title = models.CharField(max_length=200, default="Untitled Card")
    status = models.CharField(max_length=20, choices=CardStatus.choices, default=CardStatus.DRAFT)
    canvas_data = models.JSONField(
        default=dict,
        help_text="Fabric.js canvas state including text, images, and layout",
    )
    inside_message = models.TextField(blank=True)
    preview_image = models.ImageField(upload_to="piggyback/previews/", blank=True)
    is_favorite = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    def mark_sent(self):
        self.status = CardStatus.SENT
        self.sent_at = timezone.now()
        self.save(update_fields=["status", "sent_at", "updated_at"])


class CardLibraryEntry(TimeStampedModel):
    """User's card library — saved designs, sent cards, and favorites."""

    class EntryType(models.TextChoices):
        DRAFT = "draft", "Draft"
        SAVED = "saved", "Saved Design"
        SENT = "sent", "Sent Card"
        RECEIVED = "received", "Received Card"
        TEMPLATE = "template", "From Template"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="card_library",
    )
    card = models.ForeignKey(
        Card,
        on_delete=models.CASCADE,
        related_name="library_entries",
    )
    entry_type = models.CharField(max_length=20, choices=EntryType.choices)
    notes = models.TextField(blank=True)
    is_pinned = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "card library entries"
        ordering = ["-is_pinned", "-updated_at"]
        unique_together = [("user", "card", "entry_type")]

    def __str__(self):
        return f"{self.user} — {self.card.title} ({self.get_entry_type_display()})"
