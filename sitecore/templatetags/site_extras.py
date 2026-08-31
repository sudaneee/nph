from django import template

register = template.Library()


@register.filter
def absolute_url(path, request):
    """Turn a media/relative URL into an absolute one, for Open Graph / Twitter tags."""
    if not path or not request:
        return path
    return request.build_absolute_uri(path)
