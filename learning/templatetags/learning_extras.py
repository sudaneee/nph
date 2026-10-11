from django import template

register = template.Library()


@register.filter
def get_item(mapping, key):
    """Dict lookup with a variable key; quiz answers are keyed by str(question.id)."""
    if not mapping:
        return None
    return mapping.get(str(key))
