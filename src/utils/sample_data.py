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

groups = [
    {
        'name': 'Admins',
    },
    {
        'name': 'Clients',
    },
    {
        'name': 'Level 1',
    },
    {
        'name': 'Level 2',
    },
]

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
    {
        'username': 'carrier2',
        'first_name': "Carrier2",
        'last_name': "Carrier2",
        'email': "carrier2@gmail.com",
        'is_active': True,
        'is_staff': True,
        'is_superuser': False,
        'password': 'AMERICA123',
    },
    {
        'username': 'carrier3',
        'first_name': "Carrier3",
        'last_name': "Carrier3",
        'email': "carrier3@gmail.com",
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

clients_accounts = [
    {
        'username': 'usuario de Cliente de prueba',
        'first_name': "Persona",
        'last_name': "de contacto",
        'email': "unusuario@deuncliente.com",
        'is_active': True,
        'is_staff': False,
        'is_superuser': False,
        'password': 'AMERICA123',
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

zones = [
    {
        'name': 'Zona de prueba',
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
    {
        'name': 'Depósito propio',
        'address': 'Dirección propia',
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
        'street': 'Calle de prueba 1',
        'detail': '0-1',
    },
    {
        'street': 'Calle de prueba 2',
        'detail': '0-1',
    },
    {
        'street': 'Calle de prueba 3',
        'detail': '0-1',
    },
    {
        'street': 'Calle de prueba 4',
        'detail': '0-1',
    },
    {
        'street': 'Calle de prueba 5',
        'detail': '0-1',
    },
    {
        'street': 'Calle de prueba 6',
        'detail': '0-1',
    },
    {
        'street': 'Calle de prueba 7',
        'detail': '0-1',
    },
    {
        'street': 'Calle de prueba 8',
        'detail': '0-1',
    },
]
