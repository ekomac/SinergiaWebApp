from decimal import Decimal
from django.db import models
from django.conf import settings
from django.template.defaultfilters import truncatechars
from clients.models import Client, Discount
from deposit.models import Deposit
from places.models import Town

not_specified = 'No especificado'

DETAIL_CODES = {
    "0": {'multiplier': 1, 'name': 'Paquete hasta 5k'},
    "1": {'multiplier': 1.3, 'name': 'Bulto hasta 10k'},
    "2": {'multiplier': 1.6, 'name': 'Bulto hasta 20k'},
    "3": {'multiplier': 2, 'name': 'Miniflete'},
    "4": {'multiplier': 3, 'name': 'Urgente'},
    "5": {'multiplier': 1.2, 'name': 'Trámite'},
}


class Destination(models.Model):
    street = models.CharField(
        verbose_name="Domicilio de entrega", max_length=100,
        blank=False, null=False)
    remarks = models.CharField(
        verbose_name="Observaciones de entrega", max_length=500,
        blank=True, null=True)
    town = models.ForeignKey(
        Town, on_delete=models.CASCADE,
        verbose_name="Localidad de entrega", blank=False, null=False)
    zipcode = models.CharField(
        verbose_name="Cod. Postal de entrega", max_length=10,
        blank=True, null=True)

    def __str__(self):
        return self.full_address

    @property
    def full_address(self):
        return f'{self.street}, {self.zipcode} {self.town}'


class Receiver(Destination):
    name = models.CharField(
        verbose_name="Nombre destinatario", max_length=50,
        blank=True, null=True)
    doc = models.CharField(
        verbose_name="DNI destinatario", max_length=50,
        blank=True, null=True)
    phone = models.CharField(
        verbose_name="Teléfono destinatario", max_length=14,
        blank=True, null=True)

    def __str__(self):
        recipient = f'{self.name}({self.doc})' or not_specified
        address = f'{self.street}, {self.zipcode} {self.town}'
        return f'{recipient}, {address}'


class NotDeliveredYetError(Exception):
    pass


class Envio(Receiver):

    STATUS_NEW = 'N'
    STATUS_NEW_TEXT = 'Nuevo'
    STATUS_MOVING = 'M'
    STATUS_MOVING_TEXT = 'Viajando'
    STATUS_STILL = 'S'
    STATUS_STILL_TEXT = 'En depósito'
    STATUS_DELIVERED = 'D'
    STATUS_DELIVERED_TEXT = 'Entregado'

    SCHEDULE_INDEX_7_10 = '07-10'
    SCHEDULE_PHRASE_7_10 = '7 a 10 h'
    SCHEDULE_INDEX_10_13 = '10-13'
    SCHEDULE_PHRASE_10_13 = '10 a 13 h'
    SCHEDULE_INDEX_13_16 = '13-16'
    SCHEDULE_PHRASE_13_16 = '13 a 16 h'
    SCHEDULE_INDEX_16_ON = '16+'
    SCHEDULE_PHRASE_16_ON = '+16 h'

    STATUSES = [
        (STATUS_NEW, STATUS_NEW_TEXT),
        (STATUS_MOVING, STATUS_MOVING_TEXT),
        (STATUS_STILL, STATUS_STILL_TEXT),
        (STATUS_DELIVERED, STATUS_DELIVERED_TEXT),
    ]

    SCHEDULES = [
        (SCHEDULE_INDEX_7_10, SCHEDULE_PHRASE_7_10),
        (SCHEDULE_INDEX_10_13, SCHEDULE_PHRASE_10_13),
        (SCHEDULE_INDEX_13_16, SCHEDULE_PHRASE_13_16),
        (SCHEDULE_INDEX_16_ON, SCHEDULE_PHRASE_16_ON),
    ]

    date_created = models.DateTimeField(
        verbose_name="Creación", auto_now_add=True)
    date_updated = models.DateTimeField(
        auto_now=True, verbose_name="Actualización")
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        verbose_name="Editado por", related_name="envios_edited_by",
        blank=True, null=True, default=None)
    status = models.CharField(
        verbose_name="Estado",
        max_length=2, choices=STATUSES, default=STATUS_NEW)
    carrier = models.ForeignKey(
        'account.Account', related_name="envios_carried_by",
        verbose_name="Portador", blank=True, null=True,
        default=None, on_delete=models.SET_NULL)
    deposit = models.ForeignKey(
        Deposit, on_delete=models.SET_NULL,
        verbose_name="Depósito", default=None, blank=True, null=True)
    detail = models.CharField(verbose_name="Detalle",
                              max_length=200, default='0-1')
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, verbose_name="Cliente",
        blank=False, null=False)
    charge = models.IntegerField(
        verbose_name="Cargos al destinatario",
        blank=True, null=True)
    max_delivery_date = models.DateField(
        verbose_name="Fecha máxima de entrega", blank=True, null=True)
    is_flex = models.BooleanField(verbose_name="Es Flex", default=False)
    flex_id = models.CharField(
        verbose_name="ID de Flex", max_length=50, blank=True, null=True)
    delivery_schedule = models.CharField(
        verbose_name='Horario de entrega', choices=SCHEDULES,
        max_length=5, blank=True, null=True, default=None)
    bulk_upload = models.ForeignKey(
        'BulkLoadEnvios', verbose_name="ID de carga masiva",
        on_delete=models.CASCADE, blank=True, null=True)
    date_delivered = models.DateTimeField(
        verbose_name="Fecha de entrega", blank=True, null=True, default=None)
    deliverer = models.ForeignKey(
        'account.Account', related_name="envios_delivered_by",
        verbose_name="Quién lo entregó", blank=True, null=True,
        default=None, on_delete=models.SET_NULL)
    tracked = models.BooleanField(default=False)

    def __str__(self):
        address = self.full_address
        client = self.client
        status = self.get_status_display()
        if status == self.STATUS_DELIVERED:
            return f'{address} ({status}) de {client}'
        if self.carrier is not None:
            where = self.carrier
        elif self.deposit is not None:
            where = self.deposit.name
        elif self.status == self.STATUS_DELIVERED:
            where = ""
        else:
            where = not_specified
        return f'{address} @{where} ({status}) >>> {client}'

    @property
    def destination_for_client(self):
        return self.full_address + ' de ' + self.client.name

    def get_status(self):
        status = self.get_status_display()
        carrier = self.carrier
        deposit = self.deposit
        if status == self.STATUS_DELIVERED:
            return status
        if status in [self.STATUS_NEW, self.STATUS_STILL]:
            if deposit is not None:
                return f'{status}: "{deposit}"'
        if status == self.STATUS_MOVING and carrier is not None:
            return f'{status} con {carrier.username}' +\
                f' ({carrier.first_name} {carrier.last_name})'
        return status

    @property
    def readable_detail(self):
        self.get_detail_readable()

    def get_detail_readable(self):
        details = map(self.map_detail, self.detail.split(","))
        return ",".join(details)

    def map_detail(self, detail):
        parts = detail.split("-")
        index = parts[0]
        amount = parts[1]
        if index in DETAIL_CODES.keys():
            name = DETAIL_CODES[index]['name']
            return f'{amount}x {name}'.lower()

    class Meta:
        verbose_name = 'Envío'
        verbose_name_plural = 'Envíos'
        ordering = ['-date_created']

    @property
    def shimpent_type(self):
        return 'Flex' if self.is_flex else 'Mensajería'

    @property
    def price(self) -> Decimal:
        """
        Performs de calculation for the price of the 'envio'.
        It applies the discount if it is available.
        The operations are made with Decimal to avoid the rounding errors.

        Returns:
            Decimal: The price of the 'envio'.
        """
        # Get the town of recipient's address
        town = self.town

        #  Get the code. If 'envio' is from flex, return flex's code for
        # given town, else the normal code.
        code = town.flex_code if self.is_flex else town.delivery_code

        # Get the price for the given code
        price = Decimal(str(code.price))

        # Get the detail for the given envio
        detail_codes = self.detail.split(',')

        # Initialize total price to 0
        total_price = Decimal(0)

        # Get the price for each package detail
        for detail_code in detail_codes:
            # Unpack code and amount spliting by '-'
            code, amount = detail_code.split('-')
            # Get the package detail for the given code
            detail_code = DETAIL_CODES[code]
            # Get multiplier for the given package detail
            multiplier = detail_code["multiplier"]
            # Multiply the price by the multiplier for given package
            # detail, times the amount of packages
            result = Decimal(str(multiplier)) * price * Decimal(amount)
            # Add the result to the total price
            total_price += result

        # Get single discount for envio's client and partido, if and
        # only if the envio and discount match the is_for_flex and
        # is_flex flags
        discount = Discount.objects.filter(
            client__id=self.client.id,
            is_for_flex=self.is_flex,
            partidos__in=[self.town.partido]
        ).first()

        # If discount exists, apply it to the total price
        if discount:
            discount = Decimal(discount.amount) / Decimal(100)
            total_discount = total_price * discount
            result = total_price - total_discount
            return result

        # return the total price
        return total_price


def bulk_file_upload_path(instance, filename):
    author_id = str(instance.created_by.id)
    client_id = str(instance.client.id)
    client_name = str(instance.client.name)
    date = instance.date_created.strftime('%YYYY%MM%DD')
    dirs = f'bulk_loads/{author_id}/'
    file_data = f'{date}_{client_id}-{client_name}_{filename}'
    return dirs + file_data


class BulkLoadEnvios(models.Model):

    LOADING_STATUS_FINISHED = '0'
    LOADING_STATUS_PROCESSING = '1'
    LOADING_STATUS_FAILED = '2'

    LOADING_STATUSES = [
        (LOADING_STATUS_FINISHED, 'Done'),
        (LOADING_STATUS_PROCESSING, 'Loading'),
        (LOADING_STATUS_FAILED, 'Failed'),
    ]

    date_created = models.DateTimeField(
        verbose_name="Fecha de creación", auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        verbose_name="Usuario", blank=True, null=True)
    load_status = models.CharField(
        verbose_name="Estado",
        max_length=1, choices=LOADING_STATUSES,
        default=LOADING_STATUS_PROCESSING)
    client = models.ForeignKey(
        Client, on_delete=models.SET_NULL,
        verbose_name="Usuario", blank=True, null=True)
    deposit = models.ForeignKey(
        Deposit, on_delete=models.SET_NULL,
        verbose_name="Depósito", blank=True, null=True)
    csv_result = models.TextField(
        verbose_name="Resultado",
        blank=True, null=True, default=None)
    errors = models.TextField(
        verbose_name="Errores",
        blank=True, null=True, default=None)
    cells_to_paint = models.TextField(
        verbose_name="Celdas que hay que pintar",
        blank=True, null=True, default=None)
    requires_manual_fix = models.BooleanField(default=False)
    hashed_file = models.CharField(
        verbose_name="Hashed file",
        max_length=100, blank=True, null=True)
    envios_were_created = models.BooleanField(default=False)

    @property
    def short_errors_display(self):
        return truncatechars(self.errors, 100)

    @property
    def short_csv_result_display(self):
        return truncatechars(self.csv_result, 1000)

    class Meta:
        verbose_name = 'Carga masiva de envios'
        verbose_name_plural = 'Cargas masivas de envios'
