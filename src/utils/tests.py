# DJANGO
from django.contrib.auth.models import Group

# DJANGO REST FRAMEWORK
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

# PROJECT
from account.models import Account
from clients.models import Client
from deposit.models import Deposit
from envios.models import Envio
from places.models import Town, Partido, Zone
from prices.models import DeliveryCode, FlexCode
from tracking.models import TrackingMovement
from utils import sample_data as samples


class BaseMockDBTestCase(APITestCase):

    def setUp(self):
        for element in dir(self):
            if element.startswith('create_'):
                getattr(self, element)()

    def create_01_groups(self):
        self.group_admins = Group.objects.create(**samples.groups[0])
        self.group_clients = Group.objects.create(**samples.groups[1])
        self.group_employess_tier_1 = Group.objects.create(**samples.groups[2])
        self.group_employess_tier_2 = Group.objects.create(**samples.groups[3])

    def create_02_super_user(self):
        self.superuser = Account(**samples.superuser)
        self.superuser.save()
        self.superuser.groups.add(self.group_admins)
        self.superuser.save()

    def create_03_token(self):
        self.superuser_token = Token.objects.get(user__is_superuser=True)

    def create_04_delivery_codes(self):
        self.delivery_code = DeliveryCode(**samples.delivery_codes[0])
        self.delivery_code.save()

    def create_05_flex_codes(self):
        self.flex_code = FlexCode(**samples.flex_codes[0])
        self.flex_code.save()

    def create_06_zones(self):
        self.zone = Zone(**samples.zones[0])
        self.zone.save()

    def create_07_partidos(self):
        self.partido = Partido(**samples.partidos[0])
        self.partido.zone = self.zone
        self.partido.save()

    def create_08_towns(self):
        self.town_1 = Town(**samples.towns[0])
        self.town_1.partido = self.partido
        self.town_1.flex_code = self.flex_code
        self.town_1.delivery_code = self.delivery_code
        self.town_1.save()
        self.town_2 = Town(**samples.towns[1])
        self.town_2.partido = self.partido
        self.town_2.flex_code = self.flex_code
        self.town_2.delivery_code = self.delivery_code
        self.town_2.save()

    def create_09_carriers(self):
        self.carrier_1 = Account(**samples.carriers[0])
        self.carrier_1.save()
        self.carrier_1.groups.add(self.group_employess_tier_1)
        self.carrier_1.save()
        self.carrier_2 = Account(**samples.carriers[1])
        self.carrier_2.save()
        self.carrier_2.groups.add(self.group_employess_tier_2)
        self.carrier_2.save()
        self.carrier_3 = Account(**samples.carriers[2])
        self.carrier_3.save()
        self.carrier_3.groups.add(self.group_employess_tier_2)
        self.carrier_3.save()

    def create_10_clients(self):
        self.client_1 = Client(**samples.clients[0])
        self.client_1.save()

    def create_11_clients_accounts(self):
        self.client_account = Account(**samples.clients_accounts[0])
        self.client_account.client = self.client_1
        self.client_account.save()
        self.client_account.groups.add(self.group_clients)
        self.client_account.save()

    def create_12_deposits(self):
        self.deposit_1 = Deposit(**samples.deposits[0])
        self.deposit_1.client = self.client_1
        self.deposit_1.town = self.town_1
        self.deposit_1.save()
        self.deposit_2 = Deposit(**samples.deposits[1])
        self.deposit_2.town = self.town_1
        self.deposit_2.save()

    def create_13_envios(self):
        for i, envio_sample in enumerate(samples.envios):
            num = str(i + 1).zfill(2)
            setattr(self, 'envio_' + num, Envio(**envio_sample))
            getattr(self, 'envio_' + num).client = self.client_1
            getattr(self, 'envio_' + num).created_by = self.superuser
            if i < 5:
                getattr(self, 'envio_' + num).deposit = self.deposit_1
            getattr(self, 'envio_' + num).town = self.town_1
            getattr(self, 'envio_' + num).save()

    def create_14_tracking_movements(self):
        self.tracking_movement = TrackingMovement(
            created_by=self.superuser,
            action=TrackingMovement.ACTION_ADDED_TO_SYSTEM,
            result=TrackingMovement.RESULT_ADDED_TO_SYSTEM,
            deposit=self.deposit_1
        )
        self.tracking_movement.save()
        self.tracking_movement.envios.add(*[self.envio_1])


class BaseAuthorizationTestCase(APITestCase):
    """
    Test case for the authorization of the API
    """

    reverse_urls_apps = None

    def authorize(self):
        self.token = Token(user=self.superuser)
        self.token.save()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_1_no_authorization(self):
        """
        Simple test to check if the authorization is working.
        """
        if isinstance(self.reverse_urls_apps, (tuple, list)):
            for app in self.reverse_urls_apps:
                print(f"\n========== {app} ==========\n")
                if isinstance(app, (tuple, list)):
                    url_app, url_args = app
                    if isinstance(url_args, list):
                        url_args = tuple(url_args)
                    self.assertEqual(
                        self.client.get(
                            reverse(url_app, args=url_args),
                            format="json").status_code,
                        status.HTTP_401_UNAUTHORIZED
                    )
                elif isinstance(app, str):
                    self.assertEqual(
                        self.client.get(
                            reverse(app), format="json").status_code,
                        status.HTTP_401_UNAUTHORIZED
                    )

    def test_2_authorization(self):
        """
        Simple test to check if the authorization is working.
        """
        self.authorize()
        if isinstance(self.reverse_urls_apps, (tuple, list)):
            self.token = Token.objects.get(user=self.superuser)
            self.client.credentials(
                HTTP_AUTHORIZATION='Token ' + self.token.key)
            for app in self.reverse_urls_apps:
                if isinstance(app, (tuple, list)):
                    url_app, url_args = app
                    if isinstance(url_args, list):
                        url_args = tuple(url_args)
                    self.assertNotEqual(
                        self.client.get(
                            reverse(url_app, args=url_args),
                            format="json").status_code,
                        status.HTTP_401_UNAUTHORIZED
                    )
                elif isinstance(app, str):
                    self.assertNotEqual(
                        self.client.get(
                            reverse(app), format="json").status_code,
                        status.HTTP_401_UNAUTHORIZED
                    )


class BaseAuthorizationWithDBTestCase(BaseMockDBTestCase):
    """
    Test case for the authorization of the API
    """

    reverse_urls_apps = None

    def authorize(self):
        self.token = Token(user=self.superuser)
        self.token.save()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_1_no_authorization(self):
        """
        Simple test to check if the authorization is working.
        """
        if isinstance(self.reverse_urls_apps, (tuple, list)):
            for app in self.reverse_urls_apps:
                if isinstance(app, (tuple, list)):
                    url_app, url_args = app
                    if isinstance(url_args, list):
                        url_args = tuple(url_args)
                    self.assertEqual(
                        self.client.get(
                            reverse(url_app, args=url_args),
                            format="json").status_code,
                        status.HTTP_401_UNAUTHORIZED
                    )
                elif isinstance(app, str):
                    self.assertEqual(
                        self.client.get(
                            reverse(app), format="json").status_code,
                        status.HTTP_401_UNAUTHORIZED
                    )

    def test_2_authorization(self):
        """
        Simple test to check if the authorization is working.
        """
        if isinstance(self.reverse_urls_apps, (tuple, list)):
            self.token = Token.objects.get(user=self.superuser)
            self.client.credentials(
                HTTP_AUTHORIZATION='Token ' + self.token.key)
            for app in self.reverse_urls_apps:
                if isinstance(app, (tuple, list)):
                    url_app, url_args = app
                    if isinstance(url_args, list):
                        url_args = tuple(url_args)
                    self.assertNotEqual(
                        self.client.get(
                            reverse(url_app, args=url_args),
                            format="json").status_code,
                        status.HTTP_401_UNAUTHORIZED
                    )
                elif isinstance(app, str):
                    self.assertNotEqual(
                        self.client.get(
                            reverse(app), format="json").status_code,
                        status.HTTP_401_UNAUTHORIZED
                    )


class SimpleAuthorizedMockDBAPITestCase(BaseMockDBTestCase):

    reverse_to_app = None

    def setUp(self):
        for element in dir(self):
            if element.startswith('create_'):
                getattr(self, element)()
        self.setup_url()

    def get_reverse_to_app(self):
        return self.reverse_to_app

    def create_01_groups(self):
        self.group_admins = Group.objects.create(**samples.groups[0])
        self.group_clients = Group.objects.create(**samples.groups[1])
        self.group_employess_tier_1 = Group.objects.create(**samples.groups[2])
        self.group_employess_tier_2 = Group.objects.create(**samples.groups[3])

    def create_02_super_user(self):
        self.superuser = Account(**samples.superuser)
        self.superuser.save()
        self.superuser.groups.add(self.group_admins)
        self.superuser.save()

    def create_03_token(self):
        self.superuser_token = Token.objects.get(user__is_superuser=True)

    def create_04_delivery_codes(self):
        self.delivery_code = DeliveryCode(**samples.delivery_codes[0])
        self.delivery_code.save()

    def create_05_flex_codes(self):
        self.flex_code = FlexCode(**samples.flex_codes[0])
        self.flex_code.save()

    def create_06_zones(self):
        self.zone = Zone(**samples.zones[0])
        self.zone.save()

    def create_07_partidos(self):
        self.partido = Partido(**samples.partidos[0])
        self.partido.zone = self.zone
        self.partido.save()

    def create_08_towns(self):
        self.town_1 = Town(**samples.towns[0])
        self.town_1.partido = self.partido
        self.town_1.flex_code = self.flex_code
        self.town_1.delivery_code = self.delivery_code
        self.town_1.save()
        self.town_2 = Town(**samples.towns[1])
        self.town_2.partido = self.partido
        self.town_2.flex_code = self.flex_code
        self.town_2.delivery_code = self.delivery_code
        self.town_2.save()

    def create_09_carriers(self):
        self.carrier_1 = Account(**samples.carriers[0])
        self.carrier_1.save()
        self.carrier_1.groups.add(self.group_employess_tier_1)
        self.carrier_1.save()
        self.carrier_2 = Account(**samples.carriers[1])
        self.carrier_2.save()
        self.carrier_2.groups.add(self.group_employess_tier_2)
        self.carrier_2.save()
        self.carrier_3 = Account(**samples.carriers[2])
        self.carrier_3.save()
        self.carrier_3.groups.add(self.group_employess_tier_2)
        self.carrier_3.save()

    def create_10_clients(self):
        self.client_1 = Client(**samples.clients[0])
        self.client_1.save()

    def create_11_clients_accounts(self):
        self.client_account = Account(**samples.clients_accounts[0])
        self.client_account.client = self.client_1
        self.client_account.save()
        self.client_account.groups.add(self.group_clients)
        self.client_account.save()

    def create_12_deposits(self):
        self.deposit_1 = Deposit(**samples.deposits[0])
        self.deposit_1.client = self.client_1
        self.deposit_1.town = self.town_1
        self.deposit_1.save()
        self.deposit_2 = Deposit(**samples.deposits[1])
        self.deposit_2.town = self.town_1
        self.deposit_2.save()

    def create_13_envios(self):
        for i, envio_sample in enumerate(samples.envios):
            num = str(i + 1)
            setattr(self, 'envio_' + num, Envio(**envio_sample))
            getattr(self, 'envio_' + num).client = self.client_1
            getattr(self, 'envio_' + num).created_by = self.superuser
            if i < 5:
                getattr(self, 'envio_' + num).deposit = self.deposit_1
            getattr(self, 'envio_' + num).town = self.town_1
            getattr(self, 'envio_' + num).save()

    def create_14_tracking_movements(self):
        self.tracking_movement = TrackingMovement(
            created_by=self.superuser,
            action=TrackingMovement.ACTION_ADDED_TO_SYSTEM,
            result=TrackingMovement.RESULT_ADDED_TO_SYSTEM,
            deposit=self.deposit_1
        )
        self.tracking_movement.save()
        self.tracking_movement.envios.add(*[self.envio_1])

    def setup_url(self):
        reverse_to_app = self.get_reverse_to_app()
        if reverse_to_app is None:
            raise ValueError('reverse_to_app is not defined')
        if isinstance(reverse_to_app, (tuple, list)):
            to_app, args = reverse_to_app
            if isinstance(args, list):
                args = tuple(args)
            else:
                raise TypeError(
                    "The args must be a list or tuple")
            self.url = reverse(to_app, args=args)
        else:
            self.url = reverse(self.reverse_to_app)

    def test_00a_no_authorization(self):
        """
        Simple test to check if the authorization is working.
        """
        self.assertEqual(
            self.client.get(
                reverse(self.reverse_to_app), format="json").status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_00b_authorization(self):
        """
        Simple test to check if the authorization is working.
        """
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.superuser_token.key)
        self.assertNotEqual(
            self.client.get(
                reverse(self.reverse_to_app), format="json").status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def post(self, data={}):
        return self.client.post(self.url, data, format='json')

    def get(self):
        return self.client.get(self.url, format='json')
