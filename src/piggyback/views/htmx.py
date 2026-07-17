"""Helpers for HTMX partial rendering."""

from django.shortcuts import render


def is_htmx(request) -> bool:
    return request.headers.get("HX-Request") == "true"


def htmx_template_names(request, partial: str, full: str) -> list[str]:
    return [partial] if is_htmx(request) else [full]


def render_partial(request, template_name: str, context: dict | None = None):
    return render(request, template_name, context or {})
