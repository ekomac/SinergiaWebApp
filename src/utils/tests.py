from account.models import Account
from account.tests import carriers_samples as carriers
from clients.models import Client
from clients.tests import samples as clients
from deposit.models import Deposit
from deposit.tests import samples as deposits
from envios.models import Envio
from envios.tests import samples as envios
from places.models import Town, Partido
from places.tests import town_samples as towns, partido_samples as partidos
from prices.models import DeliveryCode, FlexCode
from places.tests import (
    deliverycode_samples as delivery_codes,
    flexcode_samples as flex_codes
)


class Samples:

    ARG_CARRIER = 1
    ARG_CLIENT = 2
    ARG_DEPOSIT = 3
    ARG_ENVIO = 4
    ARG_TOWN = 5
    ARG_PARTIDO = 6
    ARG_DELIVERY_CODE = 7
    ARG_FLEX_CODE = 8

    def __init__(self):
        self.carriers = carriers
        self.clients = clients
        self.deposits = deposits
        self.envios = envios
        self.towns = towns
        self.partidos = partidos
        self.delivery_codes = delivery_codes
        self.flex_codes = flex_codes

    @property
    def all_args(self):
        return [
            self.ARG_CARRIER,
            self.ARG_CLIENT,
            self.ARG_DEPOSIT,
            self.ARG_ENVIO,
            self.ARG_TOWN,
            self.ARG_PARTIDO,
            self.ARG_DELIVERY_CODE,
            self.ARG_FLEX_CODE,
        ]

    def sample(self, *args):
        for arg in args:
            if arg not in self.all_args:
                raise ValueError(f'Invalid sample argument: {arg}')
        
        return args[0]
