from django import template

register = template.Library()

@register.filter
def mul(value, arg):
    """Multiply value by arg (for price × quantity)."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ""
