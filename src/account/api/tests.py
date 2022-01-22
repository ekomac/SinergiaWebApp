from rest_framework import status
from utils.tests import BaseAuthorizationTestCase, SimpleAuthorizedMockDBAPITestCase


class AuthorizationTestCase(BaseAuthorizationTestCase):
    reverse_urls_apps = (
        'account-api:carriers',
        'account-api:employees-with-envios',
    )


class CarriersTestCase(SimpleAuthorizedMockDBAPITestCase):

    reverse_to_app = 'account-api:carriers'

    def test_01_get_carriers_ok(self):
        # self.create_db()
        # self.login()
        self.envio_1.carrier = self.carrier_1
        self.envio_1.save()
        self.envio_2.carrier = self.carrier_2
        self.envio_2.save()
        response = self.get()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)
        self.assertEqual(self.carrier_1.username,
                         response.data["results"][0]['username'])
        self.assertEqual(self.carrier_2.email,
                         response.data["results"][1]['email'])


class EmployeesWithEnviosTestCase(SimpleAuthorizedMockDBAPITestCase):

    reverse_to_app = 'account-api:employees-with-envios'

    def test_01_get_employees_ok(self):
        response = self.get()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 4)

    def test_02_get_employees_with_at_least_one_envio(self):
        self.envio_1.carrier = self.carrier_1
        self.envio_1.save()
        self.envio_2.carrier = self.carrier_2
        self.envio_2.save()
        self.envio_3.carrier = self.carrier_2
        self.envio_3.save()
        response = self.get()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 4)
        self.assertEqual(response.data["results"][0]['envios'], 2)
        self.assertEqual(response.data["results"]
                         [0]['username'], self.carrier_2.username)
        self.assertEqual(response.data["results"][1]['envios'], 1)
        self.assertEqual(response.data["results"]
                         [1]['username'], self.carrier_1.username)

    def test_03_get_employees_with_envios_as_ordering(self):
        self.envio_1.carrier = self.carrier_1
        self.envio_1.save()
        self.envio_2.carrier = self.carrier_2
        self.envio_2.save()
        self.envio_3.carrier = self.carrier_2
        self.envio_3.save()
        response = self.get()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 4)
        self.assertEqual(response.data["results"][0]['envios'], 2)
        self.assertEqual(response.data["results"]
                         [0]['username'], self.carrier_2.username)
        self.assertEqual(response.data["results"][1]['envios'], 1)
        self.assertEqual(response.data["results"]
                         [1]['username'], self.carrier_1.username)
