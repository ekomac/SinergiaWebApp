from random import sample
from typing import List
from account.models import Account
from clients.models import Client
from deposit.models import Deposit
from envios.models import Envio
from places.models import Town, Partido
from prices.models import DeliveryCode, FlexCode
from tracking.models import TrackingMovement
from utils import sample_data as samples


class SimpleMockDB:

    MIN_SAMPLE_QUANTITY = 1
    MAX_SAMPLE_QUANTITY = 1
    samples_quantity = MIN_SAMPLE_QUANTITY

    def __init__(self):
        if self.samples_quantity > self.MAX_SAMPLE_QUANTITY:
            raise ValueError(
                f'{self.__class__.__name__} samples_quantity must be less ' +
                f'or equal than {self.MAX_SAMPLE_QUANTITY}'
            )
        elif self.samples_quantity < self.MIN_SAMPLE_QUANTITY:
            raise ValueError(
                f'{self.__class__.__name__} samples_quantity must be ' +
                f'greater or equal than {self.MIN_SAMPLE_QUANTITY}'
            )
        else:
            self._accounts = []
            self._delivery_codes = []
            self._flex_codes = []
            self._partidos = []
            self._towns = []
            self._clients = []
            self._deposits = []
            self._envios = []
            self._trackingmovements = []

    def create(self) -> None:
        """
        Creates all the objects required for the tests.
        """
        self.superadmin = Account(**samples.superuser)
        self.accounts.append(self.superadmin)

        for i in range(self.MIN_SAMPLE_QUANTITY, self.samples_quantity):
            delivery_code = DeliveryCode(**samples.delivery_codes[i]).save()
            flex_code = FlexCode(**samples.flex_codes[i]).save()
            partido = Partido(**samples.partidos[i]).save()
            town = Town(partido=partido, **samples.towns[i]).save()
            carrier = Account(**samples.carriers[i]).save()
            client = Client(**samples.clients[i]).save()
            deposit = Deposit(client=client, **samples.deposits[i]).save()
            envio = Envio(client=client, created_by=self.superuser,
                          **samples.envios[i]).save()

            tracking_movement = TrackingMovement(
                created_by=self.superuser,
                action=TrackingMovement.ACTION_ADDED_TO_SYSTEM,
                result=TrackingMovement.RESULT_ADDED_TO_SYSTEM,
                deposit=envio.deposit
            )
            tracking_movement.save()
            tracking_movement.envios.add(*[envio])

            self._delivery_codes.append(delivery_code)
            self._flex_codes.append(flex_code)
            self._partidos.append(partido)
            self._towns.append(town)
            self._accounts.append(carrier)
            self._clients.append(client)
            self._deposits.append(deposit)
            self._envios.append(envio)
            self._trackingmovements.append(tracking_movement)

            print("delivery_codes", self.delivery_codes)
            print("flex_codes", self.flex_codes)
            print("partidos", self.partidos)
            print("towns", self.towns)
            print("clients", self.clients)
            print("deposits", self.deposits)
            print("envios", self.envios)
            print("trackingmovements", self.trackingmovements)

    @property
    def accounts(self) -> List[Account]:
        return self._accounts

    @property
    def clients(self) -> List[Client]:
        return self._clients

    @property
    def deposits(self) -> List[Deposit]:
        return self._deposits

    @property
    def envios(self) -> List[Envio]:
        return self._envios

    @property
    def towns(self) -> List[Town]:
        return self._towns

    @property
    def partidos(self) -> Partido:
        return self._partidos

    @property
    def delivery_codes(self) -> DeliveryCode:
        return self._delivery_codes

    @property
    def flex_codes(self) -> FlexCode:
        return self.flex_codes
