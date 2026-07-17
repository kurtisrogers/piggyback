# syntax=docker/dockerfile:1

FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DJANGO_SETTINGS_MODULE=example.settings

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libjpeg62-turbo-dev \
        zlib1g-dev \
        libpq-dev \
        gcc \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md LICENSE ./
COPY src ./src
COPY example ./example
COPY scripts/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh

ENV PYTHONPATH="/app/src:/app"

RUN pip install --upgrade pip \
    && pip install -e ".[docker]" \
    && chmod +x /usr/local/bin/docker-entrypoint.sh \
    && python example/manage.py collectstatic --noinput

RUN useradd --create-home --uid 10001 appuser \
    && mkdir -p /app/media /app/data \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["gunicorn", "example.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120"]
