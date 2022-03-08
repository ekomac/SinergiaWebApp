from django import template

register = template.Library()


@register.filter
def truncate_start(s: str, max_length=30) -> str:
    """Truncates the given string to the last <max_length> characters,
    unless it contains a slash, in which case it truncates to the last.

    Args:
        s (str): the string to be truncated.
        max_length (int): max chars in the resulting str. Defaults to 30.

    Returns:
        str: the truncated string.
    """
    if '/' in s:
        return ".../" + s[s.rfind('/') + 1:]
    elif len(s) > max_length:
        return "..." + s[-max_length:]
    return s
