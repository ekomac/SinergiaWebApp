from django import template

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
