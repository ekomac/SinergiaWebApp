from decimal import Decimal


superuser = {
    'username': 'superadmin',
    'first_name': "Juan Cruz",
    'last_name': "Maciel Henning",
    'email': "jcmacielhenning@gmail.com",
    'is_active': True,
    'is_staff': True,
    'is_superuser': True,
    'password': 'AMERICA123',
}

carriers = [
    {
        'username': 'carrier',
        'first_name': "Carrier",
        'last_name': "Carrier",
        'email': "carrier@gmail.com",
        'is_active': True,
        'is_staff': True,
        'is_superuser': False,
        'password': 'AMERICA123',
    },
]

clients = [
    {
        'name': 'Cliente de prueba',
        'contact_name': 'Persona de contacto',
        'contact_phone': 'Número de teléfono',
        'contact_email': 'email@email.com',
    },
]

towns = [
    {
        'name': 'Ciudad de prueba',
    },
    {
        'name': 'Ciudad de prueba N° 2',
    },
]

partidos = [
    {
        'name': 'Partido de prueba',
    },
]

deposits = [
    {
        'name': 'Depósito de prueba',
        'address': 'Dirección de prueba',
    },
]

delivery_codes = [
    {'code': 'M01', 'price': Decimal("30.00")},
]

flex_codes = [
    {'code': 'F01', 'price': Decimal("80.00")},
]

envios = [
    {
        'street': 'Calle de prueba',
        'detail': '0-1',
    }
]
