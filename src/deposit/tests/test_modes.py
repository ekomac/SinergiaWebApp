from account.models import Account
from clients.models import Client
from deposit.models import Deposit
from places.models import Partido, Town
from utils.tests import SampledDataTestCase


class ClientDepositTestCase(SampledDataTestCase):

    SAMPLE_DATA = {
        Client: {'values': ({'name': 'Coca Cola'},)},
        Partido: {'values': ({'name': 'Almirante Brown', 'is_amba': True},)},
        Town: {
            'values': ({'name': 'Adrogué'},),
            'relations': {'partido': Partido}},
        Deposit: {
            'values': ({'name': 'Deposit1', 'address': 'Some street 123'},
                       {'name': 'Deposit2', 'address': 'Some street 456',
                       'zip_code': '1234'},),
            'relations': {'town': Town, 'client': Client}},
        Account: {
            'values': ({'email': 'someuser@email.com',
                        'username': 'someuser',
                        'first_name': 'Sam',
                        'last_name': 'User',
                        },),
        },
    }

    def test_str(self):
        """
        str() should return a string with the deposit name and address
        """
        deposit1 = Deposit.objects.get(name='Deposit1')
        deposit2 = Deposit.objects.get(name='Deposit2')
        self.assertEqual(
            deposit1.__str__(), ('Deposit1 en Some Street 123, '
                                 'Adrogué de Coca Cola'))
        self.assertEqual(
            deposit1.full_name(), ('Deposit1 en Some Street 123, '
                                   'Adrogué de Coca Cola'))
        self.assertEqual(
            deposit2.__str__(), ('Deposit2 en Some Street 456, '
                                 '1234 Adrogué de Coca Cola'))
        self.assertEqual(
            deposit2.full_name(), ('Deposit2 en Some Street 456, '
                                   '1234 Adrogué de Coca Cola'))

    def test_get_full_address(self):
        """
        full_address() should return a string with deposit's address
        """
        deposit1 = Deposit.objects.get(name='Deposit1')
        deposit2 = Deposit.objects.get(name='Deposit2')
        self.assertEqual(deposit1.full_address(),
                         'Some Street 123, Adrogué')
        self.assertEqual(deposit2.full_address(),
                         'Some Street 456, 1234 Adrogué')


class SinergiaDepositTestCase(SampledDataTestCase):

    SAMPLE_DATA = {
        Client: {'values': ({'name': 'Coca Cola'},)},
        Partido: {'values': ({'name': 'Almirante Brown', 'is_amba': True},)},
        Town: {
            'values': ({'name': 'Adrogué'},),
            'relations': {'partido': Partido}},
        Deposit: {
            'values': ({'name': 'Deposit1', 'address': 'Some street 123'},
                       {'name': 'Deposit2', 'address': 'Some street 456',
                        'zip_code': '1234'},),
            'relations': {'town': Town}},
        Account: {
            'values': ({'email': 'someuser@email.com',
                        'username': 'someuser',
                        'first_name': 'Sam',
                        'last_name': 'User',
                        },),
        },
    }

    def test_str(self):
        """
        str() should return a string with the deposit
        name "Sinergia" and address.
        """
        deposit1 = Deposit.objects.get(name='Deposit1')
        deposit2 = Deposit.objects.get(name='Deposit2')
        self.assertEqual(
            deposit1.__str__(), ('Deposit1 en Some Street 123, '
                                 'Adrogué de Sinergia'))
        self.assertEqual(
            deposit1.full_name(), ('Deposit1 en Some Street 123, '
                                   'Adrogué de Sinergia'))
        self.assertEqual(
            deposit2.__str__(), ('Deposit2 en Some Street 456, '
                                 '1234 Adrogué de Sinergia'))
        self.assertEqual(
            deposit2.full_name(), ('Deposit2 en Some Street 456, '
                                   '1234 Adrogué de Sinergia'))

    def test_get_full_address(self):
        """
        full_address() should return a string with deposit's address.
        """
        deposit1 = Deposit.objects.get(name='Deposit1')
        deposit2 = Deposit.objects.get(name='Deposit2')
        self.assertEqual(deposit1.full_address(),
                         'Some Street 123, Adrogué')
        self.assertEqual(deposit2.full_address(),
                         'Some Street 456, 1234 Adrogué')
