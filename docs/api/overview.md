# API Overview

Piggyback exposes a full REST API via Django REST Framework.

## Base URL

```
/api/
```

## Authentication

Session authentication is enabled by default. Authenticate via Django admin login or configure token/JWT auth in your project's `REST_FRAMEWORK` settings.

## Pagination

List endpoints are paginated (24 items per page by default).

## Filtering

Templates and assets support filtering:

```
GET /api/templates/?occasion=1&style=funny
GET /api/assets/?asset_type=sticker
```

## Content types

All write endpoints accept `application/json`.

## Error responses

Standard DRF error format:

```json
{
  "detail": "Not found."
}
```

Validation errors:

```json
{
  "card_id": ["This field is required."]
}
```
