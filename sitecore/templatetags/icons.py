from django import template
from django.utils.safestring import mark_safe

from sitecore.icons import ICONS

register = template.Library()


@register.simple_tag
def icon(name, css_class='icon', stroke_width='1.5'):
    """Render a hand-authored inline SVG icon by key. Unknown keys render nothing."""
    path = ICONS.get(name)
    if not path:
        return ''
    svg = (
        f'<svg class="{css_class}" viewBox="0 0 24 24" fill="none" '
        f'stroke="currentColor" stroke-width="{stroke_width}" '
        f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{path}</svg>'
    )
    return mark_safe(svg)
