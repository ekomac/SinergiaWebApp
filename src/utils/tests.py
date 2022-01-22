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
from places.models import Town, Partido
from prices.models import DeliveryCode, FlexCode
from tracking.models import TrackingMovement
from utils import sample_data as samples


class BaseAuthorizationTestCase(APITestCase):
    """
    Test case for the authorization of the API
    """

    reverse_urls_apps = ()

    def setUp(self):
        self.superuser = Account(**samples.superuser)
        self.superuser.save()

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
                self.assertEqual(
                    self.client.get(reverse(app), format="json").status_code,
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
                if ':' in app:
                    self.assertNotEqual(
                        self.client.get(reverse(app), format="json").status_code,
                        status.HTTP_401_UNAUTHORIZED
                    )
                elif '/' in app:
                    self.assertNotEqual(
                        self.client.get(reverse(app), format="json").status_code,
                        status.HTTP_401_UNAUTHORIZED
                    )


class SimpleMockDbTestCase(APITestCase):

    reverse_to_app = None

    def setUp(self):
        self.superuser = Account(**samples.superuser)
        self.superuser.save()
        self.group_admins = Group.objects.create(**samples.groups[0])
        self.group_clients = Group.objects.create(**samples.groups[1])
        self.group_employess_tier_1 = Group.objects.create(**samples.groups[2])
        self.group_employess_tier_2 = Group.objects.create(**samples.groups[3])
        self.superuser.groups.add(self.group_admins)
        self.superuser.save()
        self.delivery_code = DeliveryCode(**samples.delivery_codes[0])
        self.delivery_code.save()
        self.flex_code = FlexCode(**samples.flex_codes[0])
        self.flex_code.save()
        self.partido = Partido(**samples.partidos[0])
        self.partido.save()
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
        self.client_1 = Client(**samples.clients[0])
        self.client_1.save()
        self.client_account = Account(**samples.clients_accounts[0])
        self.client_account.client = self.client_1
        self.client_account.save()
        self.client_account.groups.add(self.group_clients)
        self.client_account.save()
        self.deposit_1 = Deposit(**samples.deposits[0])
        self.deposit_1.client = self.client_1
        self.deposit_1.town = self.town_1
        self.deposit_1.save()
        self.deposit_2 = Deposit(**samples.deposits[1])
        self.deposit_2.town = self.town_1
        self.deposit_2.save()
        self.envio_1 = Envio(**samples.envios[0])
        self.envio_1.client = self.client_1
        self.envio_1.created_by = self.superuser
        self.envio_1.deposit = self.deposit_1
        self.envio_1.town = self.town_1
        self.envio_1.save()
        self.envio_2 = Envio(**samples.envios[0])
        self.envio_2.client = self.client_1
        self.envio_2.created_by = self.superuser
        self.envio_2.deposit = self.deposit_1
        self.envio_2.town = self.town_1
        self.envio_2.save()
        self.envio_3 = Envio(**samples.envios[0])
        self.envio_3.client = self.client_1
        self.envio_3.created_by = self.superuser
        self.envio_3.deposit = self.deposit_1
        self.envio_3.town = self.town_2
        self.envio_3.save()
        self.envio_4 = Envio(**samples.envios[0])
        self.envio_4.client = self.client_1
        self.envio_4.created_by = self.superuser
        self.envio_4.deposit = self.deposit_1
        self.envio_4.town = self.town_2
        self.envio_4.save()

        self.tracking_movement = TrackingMovement(
            created_by=self.superuser,
            action=TrackingMovement.ACTION_ADDED_TO_SYSTEM,
            result=TrackingMovement.RESULT_ADDED_TO_SYSTEM,
            deposit=self.deposit_1
        )
        self.tracking_movement.save()
        self.tracking_movement.envios.add(*[self.envio_1])
        self.superuser_token = Token.objects.get(user__is_superuser=True)
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.superuser_token.key)

    def post(self, data={}):
        if self.reverse_to_app is None:
            raise ValueError('reverse_to_app is not defined')
        url = reverse(self.reverse_to_app)
        return self.client.post(url, data, format='json')

    def get(self, url: str = None):
        if url is None:
            if self.reverse_to_app is None:
                raise ValueError('reverse_to_app is not defined')
            url = reverse(self.reverse_to_app)
            return self.client.get(url, format='json')
        if '/' not in url:
            raise ValueError(f"Url '{url}' is invalid.")
        return self.client.get(url, format='json')
