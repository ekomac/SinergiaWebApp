from django import template


register = template.Library()


@register.filter
def verbose_name(object):
    if isinstance(object, (list, tuple)):
        object = object[0]
    if hasattr(object._meta, 'verbose_name'):
        return object._meta.verbose_name
    return type(object)


@register.filter
def verbose_name_plural(object):
    if isinstance(object, (list, tuple)):
        object = object[0]
    if hasattr(object._meta, 'verbose_name_plural'):
        return object._meta.verbose_name_plural
    return type(object)
