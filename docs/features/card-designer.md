# Card Designer

The Piggyback card editor is a browser-based design tool built on [Fabric.js](https://fabricjs.com/), with [Alpine.js](https://alpinejs.dev/) for toolbar state and [HTMX](https://htmx.org/) for the send-to-cart flow.

## Features

- **Text editing** — Add text, change fonts, sizes, and colours. Double-click for an inline Alpine overlay (no browser prompts).
- **Photo upload** — Upload personal photos and position them on the card.
- **Stickers** — Emoji sticker palette for quick decoration.
- **Backgrounds** — One-click background colour changes.
- **Inside message** — Separate inside message field for the card interior.
- **Save with feedback** — Save via API with toast notifications and status indicator.
- **Send to cart** — HTMX modal to pick recipient, delivery method, and gift add-ons.

## Canvas data format

Designs are stored as JSON in the `Card.canvas_data` field:

```json
{
  "version": "5.3.0",
  "background": "#FFF8F0",
  "objects": [
    {
      "type": "text",
      "text": "Happy Birthday!",
      "left": 874,
      "top": 400,
      "fontSize": 72,
      "fill": "#2D2D2D",
      "fontFamily": "Georgia"
    }
  ]
}
```

## Starting from a template

Templates store pre-designed `canvas_data`. When a user personalises a template, a new `Card` is created with a copy of the template's canvas state.

```python
# Via API
POST /api/templates/{slug}/personalize/

# Via URL
/editor/template/birthday-general-classic/
```

## Blank cards

Navigate to `/editor/` to start with a blank canvas.

## Headless editing

Use the REST API to create and update cards programmatically:

```bash
POST /api/cards/
{
  "title": "API Card",
  "canvas_data": {"background": "#FFF8F0", "objects": []}
}

POST /api/cards/{id}/save_design/
{
  "canvas_data": {...},
  "inside_message": "Hello from the API!"
}
```
