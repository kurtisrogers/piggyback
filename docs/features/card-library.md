# Card Library

Every user's cards are automatically organised in their personal library.

## Entry types

| Type | Description |
|------|-------------|
| `draft` | Work-in-progress designs |
| `saved` | Explicitly saved designs |
| `sent` | Cards that have been delivered |
| `received` | Cards received from others |

## Auto-sync

When `PIGGYBACK_LIBRARY_AUTO_SAVE_DRAFTS` is enabled (default), the library is kept in sync via Django signals whenever a card's status changes.

## API

```bash
# List all library entries
GET /api/library/

# Filter by type
GET /api/library/?type=draft
GET /api/library/?type=sent
```

## Web UI

Visit `/library/` to browse your cards with tabs for All, Drafts, Saved, and Sent.

## Favourites

Mark cards as favourites:

```bash
POST /api/cards/{id}/favorite/
```

Favourited cards show a pin in the library when `is_pinned` is set on the entry.
