from django.db import models

from piggyback.models.base import SluggedModel, TimeStampedModel


class OccasionCategory(SluggedModel):
    """Top-level occasion groupings — Birthday, Wedding, Sympathy, etc."""

    icon = models.CharField(max_length=64, blank=True, help_text="Emoji or icon class")
    color = models.CharField(max_length=7, default="#E85D75")
    is_featured = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta(SluggedModel.Meta):
        verbose_name_plural = "occasion categories"


class Occasion(SluggedModel):
    """Specific occasions within a category — 21st Birthday, Golden Wedding, etc."""

    category = models.ForeignKey(
        OccasionCategory,
        on_delete=models.CASCADE,
        related_name="occasions",
    )
    is_seasonal = models.BooleanField(default=False)
    month = models.PositiveSmallIntegerField(null=True, blank=True)
    day = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta(SluggedModel.Meta):
        ordering = ["category__sort_order", "name"]


class CardStyle(models.TextChoices):
    FUNNY = "funny", "Funny"
    TRADITIONAL = "traditional", "Traditional"
    PHOTO = "photo", "Photo"
    BLANK = "blank", "Blank"
    KIDS = "kids", "Kids"
    LUXURY = "luxury", "Luxury"


class CardTemplate(SluggedModel):
    """Pre-designed card templates users can personalise."""

    occasion = models.ForeignKey(
        Occasion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="templates",
    )
    style = models.CharField(
        max_length=20, choices=CardStyle.choices, default=CardStyle.TRADITIONAL
    )
    thumbnail = models.ImageField(upload_to="piggyback/templates/", blank=True)
    preview_image = models.ImageField(upload_to="piggyback/templates/", blank=True)
    canvas_data = models.JSONField(
        default=dict,
        help_text="Fabric.js canvas JSON for the template design",
    )
    is_premium = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    popularity_score = models.PositiveIntegerField(default=0)

    class Meta(SluggedModel.Meta):
        ordering = ["-popularity_score", "name"]


class DesignAsset(TimeStampedModel):
    """Stickers, backgrounds, frames, and decorative elements."""

    class AssetType(models.TextChoices):
        STICKER = "sticker", "Sticker"
        BACKGROUND = "background", "Background"
        FRAME = "frame", "Frame"
        FONT = "font", "Font"
        PATTERN = "pattern", "Pattern"

    name = models.CharField(max_length=120)
    asset_type = models.CharField(max_length=20, choices=AssetType.choices)
    image = models.ImageField(upload_to="piggyback/assets/", blank=True)
    svg_data = models.TextField(blank=True)
    tags = models.CharField(max_length=255, blank=True, help_text="Comma-separated tags")
    is_premium = models.BooleanField(default=False)

    class Meta:
        ordering = ["asset_type", "name"]

    def __str__(self):
        return f"{self.get_asset_type_display()}: {self.name}"
