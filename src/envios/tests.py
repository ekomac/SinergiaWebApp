from clients.models import Client

from envios.models import Envio
from places.models import Partido, Town
from utils.tests import SampledDataTestCase


class DestinationTestCase(SampledDataTestCase):

    SAMPLE_DATA = {
        Client: {'values': ({'name': 'Coca Cola'},)},
        Partido: {'values': ({'name': 'Almirante Brown', 'is_amba': True},)},
        Town: {
            'values': ({'name': 'Adrogué'},),
            'relations': {'partido': Partido}},
        Envio: {
            'values': ({'street': 'Calle Falsa 123', 'zipcode': '1234'},),
            'relations': {'town': Town, 'client': Client}},
    }

    def test_full_address(self):
        envio = Envio.objects.first()
        self.assertEqual(envio.full_address, 'Calle Falsa 123, 1234 Adrogué')


class ReceiverTestCase(SampledDataTestCase):

    SAMPLE_DATA = {
        Client: {'values': ({'name': 'Coca Cola'},)},
        Partido: {'values': ({'name': 'Almirante Brown', 'is_amba': True},)},
        Town: {
            'values': ({'name': 'Adrogué'},),
            'relations': {'partido': Partido}},
        Envio: {
            'values': (
                {'street': 'Calle Falsa 123', 'zipcode': '1234',
                 'name': 'Juan', 'phone': '12345678', 'doc': '50123123'},
                {'street': 'Otra calle 456', 'zipcode': '1234'},
                {'street': 'Una calle más 789',
                 'zipcode': '1234', 'name': 'María'},
            ),
            'relations': {'town': Town, 'client': Client}},
    }

    def test_str(self):
        envio1 = Envio.objects.get(street='Calle Falsa 123')
        envio2 = Envio.objects.get(street='Otra calle 456')
        envio3 = Envio.objects.get(street='Una calle más 789')
        self.assertEqual(envio1.receiver_ptr.__str__(), 'Juan (50123123)')
        self.assertEqual(envio2.receiver_ptr.__str__(), 'No especificado')
        self.assertEqual(envio3.receiver_ptr.__str__(), 'María')


class EnvioTestCase(SampledDataTestCase):

    SAMPLE_DATA = {
        Client: {'values': ({'name': 'Coca Cola'},)},
        Partido: {'values': ({'name': 'Almirante Brown', 'is_amba': True},)},
        Town: {
            'values': ({'name': 'Adrogué'},),
            'relations': {'partido': Partido}},
        Envio: {
            'values': (
                {'street': 'Calle Falsa 123', 'zipcode': '1234',
                 'name': 'Juan', 'phone': '12345678', 'doc': '50123123'},
                {'street': 'Otra calle 456', 'zipcode': '1234'},
                {'street': 'Una calle más 789',
                 'zipcode': '1234', 'name': 'María'},
            ),
            'relations': {'town': Town, 'client': Client}},
    }

    def test_str(self):
        envio1 = Envio.objects.get(street='Calle Falsa 123')
        self.assertEqual(envio1.__str__(),
                         'Calle Falsa 123, 1234 Adrogué de Coca Cola (Nuevo)')

    def test_destination_for_client(self):
        envio2 = Envio.objects.get(street='Otra calle 456')
        self.assertEqual(envio2.destination_for_client,
                         'Otra calle 456, 1234 Adrogué de Coca Cola')
