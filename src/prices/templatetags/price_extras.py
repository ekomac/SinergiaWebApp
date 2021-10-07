from django import template
from places.models import Town

register = template.Library()


@register.filter(name='multiplicado')
def multiplicado(value, arg):
    multipliers = [
        1,  # paq_5_kg
        1.3,  # bulto_10_kg
        1.6,  # bulto_20_kg
        2,  # miniflete
        3,  # urgente
        1.2,  # tramite
    ]
    result = int(value) * multipliers[arg]
    result = int(result)
    return f'{result},00'


@register.filter()
def dtowncount(value):
    """Return how many town has got given delivery code"""
    return Town.objects.filter(delivery_code__code=value).count()


@register.filter()
def ftowncount(value):
    """Return how many town has got given flex code"""
    return Town.objects.filter(flex_code__code=value).count()
