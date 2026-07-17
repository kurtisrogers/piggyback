"""Card rendering and preview generation."""

from __future__ import annotations

import io
import json
import logging

from django.core.files.base import ContentFile

logger = logging.getLogger(__name__)


def render_preview_png(card) -> bytes | None:
    """
    Render a card preview from canvas JSON.

    Uses Pillow when available; falls back to a simple placeholder image.
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        logger.warning("Pillow not installed — skipping preview render")
        return None

    from piggyback.conf import get_setting

    width = get_setting("CARD_WIDTH") // 4
    height = get_setting("CARD_HEIGHT") // 4
    img = Image.new("RGB", (width, height), color="#FFF8F0")
    draw = ImageDraw.Draw(img)

    canvas = card.canvas_data or {}
    background = canvas.get("background", "#FFF8F0")
    if isinstance(background, str) and background.startswith("#"):
        img = Image.new("RGB", (width, height), color=background)
        draw = ImageDraw.Draw(img)

    objects = canvas.get("objects", [])
    for obj in objects:
        if obj.get("type") == "text":
            text = obj.get("text", "")
            left = int(obj.get("left", 50) / 4)
            top = int(obj.get("top", 50) / 4)
            fill = obj.get("fill", "#333333")
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
            except OSError:
                font = ImageFont.load_default()
            draw.text((left, top), text, fill=fill, font=font)

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


def save_card_preview(card) -> bool:
    """Generate and attach a preview image to a card."""
    png_data = render_preview_png(card)
    if not png_data:
        return False
    filename = f"card_{card.pk}_preview.png"
    card.preview_image.save(filename, ContentFile(png_data), save=True)
    return True


def canvas_data_from_template(template) -> dict:
    """Clone template canvas data for a new card."""
    return json.loads(json.dumps(template.canvas_data or {}))


def default_blank_canvas() -> dict:
    """Starter canvas for blank card designs."""
    return {
        "version": "5.3.0",
        "background": "#FFF8F0",
        "objects": [
            {
                "type": "text",
                "text": "Your message here",
                "left": 200,
                "top": 400,
                "fontSize": 48,
                "fill": "#2D2D2D",
                "fontFamily": "Georgia",
                "originX": "center",
                "originY": "center",
            }
        ],
    }
