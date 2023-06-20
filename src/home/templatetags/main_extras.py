import re
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


@register.filter(name='has_group')
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()


@register.filter(name='is_in_list')
def is_in_list(value, given_list):
    return True if value in given_list else False


@register.filter(name='not_in_list')
def not_in_list(value, given_list):
    return True if value not in given_list else False


@register.filter(name='remove_html_tags')
def remove_html_tags(text):
    text = re.sub(r"\<\w+\>", " ", text)
    text = re.sub(r"\<\/\w+\>", " ", text)
    text = re.sub(r"\<a href=\".*\"\>", " ", text)
    return text


@register.filter(name='remove_parenthesis')
def remove_parenthesis(text: str):
    return text.replace("(", "").replace(")", "")
