from django import template

register = template.Library()


@register.filter
def pence(value):
    """Convert pence/cents integer to currency string (e.g. 299 -> 2.99)."""
    try:
        return f"{int(value) / 100:.2f}"
    except (TypeError, ValueError):
        return "0.00"
