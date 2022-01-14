from django import template

register = template.Library()


@register.filter
def comma_to_point(value):
    """Converts a comma separated string to a point separated string"""
    return str(value).replace(',', '.')
