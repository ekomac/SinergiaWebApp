from django import template
from django.template.defaultfilters import stringfilter


register = template.Library()


@register.filter
@stringfilter
def title(value: str):  # Only one argument.
    """Converts a string into title case"""
    return value.title()
