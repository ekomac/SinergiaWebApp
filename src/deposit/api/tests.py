from rest_framework import status
from django.urls import reverse
from account.models import Account
from clients.models import Client
from deposit.models import Deposit
from envios.models import Envio
from places.models import Partido, Town
from prices.models import DeliveryCode, FlexCode
from tracking.models import TrackingMovement
from utils import sample_data
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from utils.tests import BaseAuthorizationTestCase, SimpleMockDbTestCase


class AuthorizationTestCase(BaseAuthorizationTestCase):
    reverse_urls_apps = (
        'deposit-api:list',
        'deposit-api:with-envios-list',
    )


class DepositWithEnviosTestCase(SimpleMockDbTestCase):

    reverse_to_app = 'deposit-api:with-envios-list'

    def test_01_get_deposits_with_envios(self):
        response = self.get()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.deposit_1.name,
                         response.data['results'][0]['name'])
        self.assertEqual(self.deposit_1.address,
                         response.data['results'][0]['address'])
        self.assertEqual(response.data['results'][0]['envios'], 4)


class DepositFromNoClient(SimpleMockDbTestCase):

    reverse_to_app = 'deposit-api:own'

    def test_01_get_deposits_from_no_client(self):
        response = self.get()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['results'][0]['name'], self.deposit_2.name)
        self.assertEqual(
            response.data['results'][0]['address'], self.deposit_2.address)
        self.assertEqual(
            response.data['results'][0]['client']['pk'], self.deposit_2.pk)
