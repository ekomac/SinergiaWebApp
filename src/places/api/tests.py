from rest_framework import status
from utils.tests import SimpleAuthorizedMockDBAPITestCase


class TownsOfEnviosInDepositTestCase(SimpleAuthorizedMockDBAPITestCase):

    def get_reverse_to_app(self):
        return (
            'places-api:towns-of-envios-in-deposit-list',
               (self.deposit_1.pk,)
        ),

    def test_01_get_deposits_with_envios(self):
        response = self.get()
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK, "Status code is not 200")
        self.assertEqual(self.deposit_1.name,
                         response.data['results'][0]['name'],
                         "Name is not equal")
        self.assertEqual(self.deposit_1.address,
                         response.data['results'][0]['address'],
                         "Address is not equal")
        self.assertEqual(response.data['results']
                         [0]['envios'], 4,
                         "Envios is not equal")
