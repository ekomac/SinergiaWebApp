from django.contrib.auth.models import Group
from django.db.utils import IntegrityError
import os
import random
import json
from django.conf import settings
from deposit.models import Deposit
from places.models import Partido, Town, Zone, ZipCode
from prices.models import DeliveryCode, FlexCode
from account.models import Account
from clients.models import Client


def create_mensajerias(mensajerias):
    DeliveryCode.objects.bulk_create(
        [DeliveryCode(**q) for q in mensajerias]
    )
    return True


def create_flexes(flexs):
    FlexCode.objects.bulk_create(
        [FlexCode(**q) for q in flexs]
    )
    return True


def create_zones():
    Zone.objects.bulk_create(
        [Zone(name="Norte"), Zone(name="Sur"), ]
    )
    return True


def create_partidos(partidos):
    Partido.objects.bulk_create([
        Partido(name=partido, is_amba=True) for partido in partidos
    ])
    return True


def create_localidades(localidades):
    Town.objects.bulk_create(
        [Town(**q)for q in map(map_localidades, localidades)]
    )
    return True


def map_localidades(localidad):
    nombre, municipio, id_mensajeria, id_flex = tuple(localidad)
    print(nombre, municipio, id_mensajeria, id_flex)
    result = {
        'name': nombre,
        'partido': Partido.objects.get(name=municipio),
    }
    try:
        result['delivery_code'] = DeliveryCode.objects.get(code=id_mensajeria)
        result['flex_code'] = FlexCode.objects.get(code=id_flex)
    except DeliveryCode.DoesNotExist:
        print(f"DeliveryCode matching query '{id_mensajeria}' does not exist.")
    except FlexCode.DoesNotExist:
        print(f"FlexCode matching query '{id_mensajeria}' does not exist.")
    return result


def create_demo_clients(demo_clients):
    Client.objects.bulk_create(
        [Client(**q) for q in demo_clients]
    )


def create_user_groups():
    Group.objects.create(name='Admins')
    Group.objects.create(name='Clients')
    Group.objects.create(name='EmployeeTier1')
    Group.objects.create(name='EmployeeTier2')


def encode_username(first, last):
    consonants = "bcdfghjklmnpqrstvwxyz"
    result = ""
    not_used = 0
    for letter in first.lower()+last.lower():
        if letter in consonants:
            result += letter
        else:
            not_used += 1
    return result + str(not_used)


def create_users(names, lasts):
    emails = []
    for i in range(1, 20):
        while True:
            try:
                rand1 = random.randint(0, len(names) - 1)
                rand2 = random.randint(0, len(names) - 1)
                first = names[rand1]
                last = lasts[rand2]
                domain = "sinergiamensajeria.com"
                while True:
                    email = f"{first.lower()}_{last.lower()}@{domain}"
                    if email not in emails:
                        break
                username = encode_username(first, last)
                user = Account.objects.create_user(username=username,
                                                   email=email,
                                                   first_name=first,
                                                   last_name=last,
                                                   password='AMERICA123')
                user.is_superuser = False
                user.is_staff = True
                user.is_active = True
                user.save()
                if i > 15:
                    group = Group.objects.filter(
                        name='EmployeeTier1').first()
                else:
                    group = Group.objects.filter(
                        name='EmployeeTier2').first()
                user.groups.add(group)
                break
            except IntegrityError as e:
                print(e)


def create_codigos_postales():
    # Opening JSON file
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    errors_file_path = f"{BASE_DIR}\\postal_codes_bulk_result.csv"
    with open(errors_file_path, 'a') as csv:
        line = 'status,code,town\n'
    with open(BASE_DIR+'\\postal_codes.json') as file:
        # returns JSON object as a dictionary
        data = json.load(file)

        # Iterating through the json
        # list
        for obj in data['codes']:
            code = obj['code']
            town_name = obj['town']
            print("code", code, "town_name", town_name)
            zipcodes = ZipCode.objects.filter(code=code)
            print("zipcodes", zipcodes)
            if not zipcodes:
                zipcode = ZipCode(code=code)
                zipcode.save()
            else:
                zipcode = zipcodes[0]
            towns = Town.objects.filter(name=town_name.upper())
            towns = towns if towns else Town.objects.filter(
                name__contains=town_name.upper())
            if towns:
                for town in towns:
                    zipcode.towns.add(town)
                    with open(errors_file_path, 'a') as csv:
                        line = f'success,{code},\
                            "intended={town_name}{towns}"\n'
                        csv.write(line)
            else:
                with open(errors_file_path, 'a') as csv:
                    line = f'error,{code},{town_name}\n'
                    csv.write(line)
            del towns


def create_central_deposit():
    """
    Creates the central main deposit.
    """
    Deposit(
        town=Town.objects.filter(
            name='SAN MIGUEL', partido__name='SAN MIGUEL').first(),
        name='Depósito central',
        zip_code='1663',
        address='Dorrego',
        phone="+54 9 11 6649-1969",
        is_active=True,
        email="jcmacielhenning@gmail.com",
        created_by=Account.objects.filter(
            email="jcmacielhenning@gmail.com").first(),
    ).save()


def create_demo_clients_deposits(demo_clients):
    pass


def main():
    with open(settings.BASE_DIR+'\\bulk\\base_data.json') as data:
        data = json.load(data)
        mensajerias = data['mensajerias']
        flexs = data['flexs']
        partidos = data['partidos']
        localidades = data['localidades']
        demo_clients = data['demo_clients']
        demo_deposits = data['demo_deposits']
        names = data['NAMES']
        lasts = data['LASTS']
        create_mensajerias(mensajerias)
        create_flexes(flexs)
        create_zones()
        create_partidos(partidos)
        create_localidades(localidades)
        create_demo_clients(demo_clients)
        create_demo_clients_deposits(demo_deposits)
        create_codigos_postales()
        create_user_groups()
        create_users(names, lasts)
        create_central_deposit()
    return True


if __name__ == '__main__':
    main()
