from django import template


register = template.Library()


@register.filter
def to_datetime(value):  # Only one argument.
    """Converts a timestamp dict into datetime str"""
    y = value['year']
    mo = value['month']
    d = value['day']
    h = value['hour']
    m = value['minute']

    return f'{d}-{mo}-{y} {h}:{m}'


@register.filter
def bootstrap_color(value):
    """Converts a status code to a bootstrap coloring scheme name"""
    statuses = ['success', 'failed', 'neutral']
    bcoloring = ['success', 'danger', 'primary']
    try:
        i = statuses.index(value)
        return bcoloring[i]
    except ValueError:
        return 'primary'


@register.filter
def comma_to_point(value):
    """Converts a comma separated string to a point separated string"""
    return str(value).replace(',', '.')
