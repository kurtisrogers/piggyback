# Frontend (HTMX & Alpine.js)

Piggyback's web UI uses [HTMX](https://htmx.org/) for server-driven partial updates and [Alpine.js](https://alpinejs.dev/) for lightweight client-side UI state — no React, no build step.

## Stack

| Layer | Technology | Role |
|-------|------------|------|
| Templates | Django | Server-rendered HTML |
| Interactivity | HTMX 2 | Partial page swaps, form posts, deletes |
| UI state | Alpine.js 3 | Modals, toasts, editor toolbar |
| Canvas | Fabric.js 5 | Card designer (editor only) |

Both HTMX and Alpine are loaded from CDN in `base.html`. CSRF tokens are sent automatically via `hx-headers`.

## HTMX patterns

### Catalog & library filters

Filter links use `hx-get` to fetch partial templates without a full page reload:

```html
<a hx-get="?occasion=birthday"
   hx-target="#template-grid"
   hx-select="#template-grid"
   hx-swap="outerHTML"
   hx-push-url="true">Birthday</a>
```

The server returns `partials/template_grid.html` when the `HX-Request` header is present.

### Recipients & reminders CRUD

Add/delete forms post to dedicated views and swap `#recipients-panel` or `#reminders-panel`:

- `POST /recipients/add/` — create recipient
- `DELETE /recipients/<id>/delete/` — remove recipient
- `POST /reminders/add/` — create reminder
- `DELETE /reminders/<id>/delete/` — remove reminder

### Cart

- Promo codes apply inline via `hx-post` (no redirect)
- Remove items with `hx-delete` on `/cart/remove/<item_id>/`

### Send card flow

The editor's **Send Card** button loads a modal partial via HTMX. Submitting the form calls `add_card_to_cart()` and redirects to the cart.

## Alpine.js patterns

### Global toasts

Dispatch from anywhere:

```javascript
window.dispatchEvent(new CustomEvent('pb-toast', {
  detail: { message: 'Card saved!', type: 'success' }
}));
```

The toast container in `base.html` listens via `@pb-toast.window`.

### Card editor

The editor uses Alpine for:

- Save status and loading state
- Inline text editing overlay (replaces `prompt()`)
- Send card modal visibility

Fabric.js still handles all canvas manipulation.

## Partials directory

```
templates/piggyback/partials/
├── template_grid.html
├── catalog_pagination.html
├── library_grid.html
├── recipients_panel.html
├── recipient_form.html
├── recipient_list.html
├── reminders_panel.html
├── reminder_form.html
├── reminder_list.html
├── cart_content.html
└── send_card_modal.html
```

## Navigation boost

Main nav links use `hx-boost="true"` for faster page transitions. The card editor is excluded (complex JS lifecycle).

## Extending

To add a new HTMX endpoint:

1. Create a partial template under `partials/`
2. Add a view that returns the partial when `HX-Request` is set (see `piggyback.views.htmx.is_htmx`)
3. Wire `hx-get` / `hx-post` attributes in the template

For client-only state (toggles, modals), use Alpine `x-data` on the relevant container.
