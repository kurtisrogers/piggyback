# Docker

Run the Piggyback demo app in Docker with one command.

## Quick start (SQLite)

```bash
docker compose up --build
```

Open [http://localhost:8000](http://localhost:8000)

**Demo login:** `demo` / `demo12345` at `/admin/login/`

The container automatically:

1. Runs migrations
2. Loads sample card fixtures
3. Creates/updates the demo superuser
4. Starts Gunicorn on port 8000

## PostgreSQL (optional)

For a production-like database:

```bash
docker compose --profile postgres up --build web-postgres db
```

This starts Postgres 16 and the app configured to use it.

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DJANGO_SECRET_KEY` | dev key | Django secret key |
| `DJANGO_DEBUG` | `true` | Debug mode |
| `DJANGO_ALLOWED_HOSTS` | `*` | Comma-separated hosts |
| `PIGGYBACK_PUBLIC_URL` | `http://localhost:8000` | Public URL for e-card links |
| `DATABASE_PATH` | `/app/db.sqlite3` | SQLite path (default compose uses `/app/data/db.sqlite3`) |
| `POSTGRES_HOST` | — | Enable Postgres when set (e.g. `db`) |
| `POSTGRES_DB` | `piggyback` | Postgres database name |
| `POSTGRES_USER` | `piggyback` | Postgres user |
| `POSTGRES_PASSWORD` | `piggyback` | Postgres password |
| `LOAD_SAMPLE_DATA` | `true` | Load fixtures on startup |
| `CREATE_DEMO_USER` | `true` | Create demo superuser on startup |
| `DEMO_USERNAME` | `demo` | Demo admin username |
| `DEMO_PASSWORD` | `demo12345` | Demo admin password |

## Volumes

Default compose persists:

- `piggyback_data` — SQLite database
- `piggyback_media` — uploaded images and card previews

## Build image only

```bash
docker build -t piggyback:latest .
docker run --rm -p 8000:8000 piggyback:latest
```

## Development without Docker

See [Quick Start](getting-started/quickstart.md).
