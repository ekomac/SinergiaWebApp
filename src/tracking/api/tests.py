from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase
from account.models import Account
from account.tests import carriers_samples as carriers
from clients.models import Client
from clients.tests import samples as clients
from deposit.models import Deposit
from envios.models import Envio
from tracking.models import TrackingMovement


class WithdrawAllTestCase(APITestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.carrier = Account(**carriers[0])
        self.client = Client(**clients[0])
        self.deposit = Deposit(
            client=self.client,
            name=f'Deposito {self.client.name}',
            address="Avenida de prueba 123"
        )
        print(self.deposit)
        # self.envio = Envio(
        #     street="Calle de prueba 123",
        #     town
        # )

    def test_withdraw_all_no_superuser(self):
        pass
        # carrier = self.carrier.id
        # deposit = self.deposit.id
        # url = reverse('tracking:api:withdraw-all')
        # data = {
        #     'action': TrackingMovement.ACTION_WITHDRAW,
        #     'result': TrackingMovement.RESULT_SUCCESS,
        # }
        # response = self.client.post(url, data, format='json')
        # self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # self.assertEqual(TrackingMovement.objects.count(), 1)
        # self.assertEqual(TrackingMovement.objects.get().action,
        #                  TrackingMovement.ACTION_WITHDRAW)
        # self.assertEqual(TrackingMovement.objects.get().result,
        #                  TrackingMovement.RESULT_SUCCESS)
