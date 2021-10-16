from django import template
from django.template.defaultfilters import stringfilter
from places.models import Zone


register = template.Library()


@register.filter
@stringfilter
def title(value: str):  # Only one argument.
    """Converts a string into title case"""
    return value.title()


@register.filter
def cant_partidos(value: Zone) -> str:  # Only one argument.
    """Returns the amount of partidos in a zone as a str"""
    print(value)
    count = value.partido_set.count()
    return str(count)
