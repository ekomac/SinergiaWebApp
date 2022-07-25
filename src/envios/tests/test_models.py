from account.models import Account
from clients.models import Client
from deposit.models import Deposit

from envios.models import Envio
from places.models import Partido, Town
from utils.tests import SampledDataTestCase


BASE_SAMPLE_DATA = {
    Client: {'values': ({'name': 'Coca Cola'},)},
    Partido: {'values': ({'name': 'Almirante Brown', 'is_amba': True},)},
    Town: {
        'values': ({'name': 'Adrogué'},),
        'relations': {'partido': Partido}},
    Deposit: {
        'values': ({'name': 'Deposit1', 'address': 'Some street 123'},),
        'relations': {'town': Town, 'client': Client}},
    Envio: {
        'values': (
            {'street': 'Calle Falsa 123', 'zipcode': '1234',
             'name': 'Juan', 'phone': '12345678', 'doc': '50123123'},
            {'street': 'Otra calle 456', 'zipcode': '1234'},
            {'street': 'Una calle más 789',
             'zipcode': '1234', 'name': 'María'},
        ),
        'relations': {'town': Town, 'client': Client}},
    Account: {
        'values': ({'email': 'someuser@email.com',
                    'username': 'someuser',
                    'first_name': 'Sam',
                    'last_name': 'User',
                    },),
    },
}


class BaseEnvioAppTest(SampledDataTestCase):

    SAMPLE_DATA = BASE_SAMPLE_DATA


class DestinationTestCase(BaseEnvioAppTest):

    def test_full_address(self):
        envio = Envio.objects.get(street='Calle Falsa 123')
        self.assertEqual(envio.full_address, 'Calle Falsa 123, 1234 Adrogué')


class ReceiverTestCase(BaseEnvioAppTest):

    def test_str(self):
        envio1 = Envio.objects.get(street='Calle Falsa 123')
        envio2 = Envio.objects.get(street='Otra calle 456')
        envio3 = Envio.objects.get(street='Una calle más 789')
        self.assertEqual(envio1.receiver_ptr.__str__(), 'Juan (50123123)')
        self.assertEqual(envio2.receiver_ptr.__str__(), 'No especificado')
        self.assertEqual(envio3.receiver_ptr.__str__(), 'María')


class EnvioTestCase(BaseEnvioAppTest):

    def test_str(self):
        envio = Envio.objects.get(street='Calle Falsa 123')
        self.assertEqual(envio.__str__(),
                         'Calle Falsa 123, 1234 Adrogué de Coca Cola (Nuevo)')

    def test_destination_for_client(self):
        envio = Envio.objects.get(street='Otra calle 456')
        self.assertEqual(envio.destination_for_client,
                         'Otra calle 456, 1234 Adrogué de Coca Cola')

    def test_get_status_delivered(self):
        envio = Envio.objects.get(street='Otra calle 456')
        envio.status = Envio.STATUS_DELIVERED
        self.assertEqual(envio.get_status(),
                         Envio.STATUS_DELIVERED_TEXT)

    def test_get_status_new(self):
        envio = Envio.objects.get(street='Otra calle 456')
        envio.status = Envio.STATUS_NEW
        deposit = Deposit.objects.filter(name='Deposit1').first()
        envio.deposit = deposit
        status = envio.get_status()
        expected_result = Envio.STATUS_NEW_TEXT +\
            ': Deposit1 en Some Street 123, Adrogué de Coca Cola'
        self.assertEqual(status, expected_result)

    def test_get_status_still(self):
        envio = Envio.objects.get(street='Otra calle 456')
        envio.status = Envio.STATUS_STILL
        self.assertEqual(envio.get_status(), Envio.STATUS_STILL_TEXT)
        deposit = Deposit.objects.filter(name='Deposit1').first()
        envio.deposit = deposit
        envio.save()
        expected_result = Envio.STATUS_STILL_TEXT +\
            ': Deposit1 en Some Street 123, Adrogué de Coca Cola'
        self.assertEqual(envio.get_status(), expected_result)

    def test_get_status_moving(self):
        envio = Envio.objects.get(street='Otra calle 456')
        envio.status = Envio.STATUS_MOVING
        self.assertEqual(envio.get_status(), Envio.STATUS_MOVING_TEXT)
        carrier = Account.objects.filter(username='someuser').first()
        envio.carrier = carrier
        status = envio.get_status()
        expected_result = Envio.STATUS_MOVING_TEXT + \
            ' con @someuser (Sam User)'
        self.assertEqual(status, expected_result)

    def test_get_status_default(self):
        envio = Envio.objects.get(street='Otra calle 456')
        envio.status = Envio.STATUS_NEW
        self.assertEqual(envio.get_status(), Envio.STATUS_NEW_TEXT)
        envio.status = Envio.STATUS_MOVING
        self.assertEqual(envio.get_status(), Envio.STATUS_MOVING_TEXT)
        envio.status = Envio.STATUS_STILL
        self.assertEqual(envio.get_status(), Envio.STATUS_STILL_TEXT)
        envio.status = Envio.STATUS_DELIVERED
        self.assertEqual(envio.get_status(), Envio.STATUS_DELIVERED_TEXT)
        envio.status = Envio.STATUS_RETURNED
        self.assertEqual(envio.get_status(), Envio.STATUS_RETURNED_TEXT)
        envio.status = Envio.STATUS_CANCELED
        self.assertEqual(envio.get_status(), Envio.STATUS_CANCELED_TEXT)
