from rest_framework import status
from utils.tests import BaseAuthorizationTestCase, SimpleMockDbTestCase


class AuthorizationTestCase(BaseAuthorizationTestCase):
    reverse_urls_apps = (
        'places-api:towns-of-envios-in-deposit-list',
    )


class TownOfEnviosInDepositTestCase(SimpleMockDbTestCase):

    reverse_to_app = 'deposit-api:with-envios-list'

    def test_01_get_deposits_with_envios(self):
        response = self.get('/places-api/towns-of-envios-in-deposit-list/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.deposit_1.name,
                         response.data['results'][0]['name'])
        self.assertEqual(self.deposit_1.address,
                         response.data['results'][0]['address'])
        self.assertEqual(response.data['results'][0]['envios'], 4)
