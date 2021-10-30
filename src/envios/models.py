from decimal import Decimal
from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.template.defaultfilters import truncatechars
from simple_history.models import HistoricalRecords
from clients.models import Client
from places.models import Town


def upload_location(instance, filename, *args, **kwargs):
    client_id = str(instance.client.id)
    client_name = str(instance.client.name)
    envio_id = str(instance.id)
    return f'envios/{client_id}-{client_name}/{envio_id}-{filename}'


class Envio(models.Model):

    STATUS_NEW = 'N'
    STATUS_MOVING = 'M'
    STATUS_STILL = 'S'
    STATUS_DELIVERED = 'D'

    STATUSES = [
        (STATUS_NEW, 'Nuevo'),
        (STATUS_MOVING, 'Viajando'),
        (STATUS_STILL, 'En depósito'),
        (STATUS_DELIVERED, 'Entregado'),
    ]

    SCHEDULES = [
        ('07-10', '7 a 10 h'),
        ('10-13', '10 a 13 h'),
        ('13-16', '13 a 16 h'),
        ('16+', '+16 h'),
    ]

    date_created = models.DateTimeField(
        verbose_name="Fecha de creación", auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        verbose_name="Usuario", blank=False, null=False)
    shipment_status = models.CharField(
        verbose_name="Estado",
        max_length=2, choices=STATUSES, default=STATUS_NEW)
    detail = models.CharField(verbose_name="Detalle",
                              max_length=2000, default='0-1')
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, verbose_name="Cliente",
        blank=False, null=False)
    recipient_name = models.CharField(
        verbose_name="Nombre destinatario", max_length=50,
        blank=True, null=True)
    recipient_doc = models.CharField(
        verbose_name="DNI destinatario", max_length=50,
        blank=True, null=True)
    recipient_phone = models.CharField(
        verbose_name="Teléfono destinatario", max_length=14,
        blank=True, null=True)
    recipient_address = models.CharField(
        verbose_name="Domicilio de entrega", max_length=100,
        blank=False, null=False)
    recipient_entrances = models.CharField(
        verbose_name="Observaciones de entrega", max_length=500,
        blank=True, null=True)
    recipient_town = models.ForeignKey(
        Town, on_delete=models.CASCADE,
        verbose_name="Localidad de entrega", blank=False, null=False)
    recipient_zipcode = models.CharField(
        verbose_name="Cod. Postal de entrega", max_length=10,
        blank=True, null=True)
    recipient_charge = models.DecimalField(
        verbose_name="Cargos al destinatario",
        decimal_places=2, max_digits=40, blank=True, null=True)
    max_delivery_date = models.DateField(
        verbose_name="Fecha máxima de entrega", blank=True, null=True)
    is_flex = models.BooleanField(verbose_name="Es Flex", default=False)
    flex_id = models.CharField(
        verbose_name="ID de Flex", max_length=50, blank=True, null=True)
    delivery_schedule = models.CharField(
        verbose_name='Horario de entrega', choices=SCHEDULES,
        max_length=5, blank=True, null=True)
    bulk_upload_id = models.ForeignKey(
        'BulkLoadEnvios', verbose_name="ID de carga masiva",
        on_delete=models.SET_NULL, blank=True, null=True)
    history = HistoricalRecords()

    def __str__(self):
        address = self.recipient_address
        town = self.recipient_town.name
        client = self.client
        return f'{address}, {town.title()} from {client}'

    class Meta:
        verbose_name = 'Envío'
        verbose_name_plural = 'Envíos'


def base_create_tracking(instance: Envio) -> None:
    deposit = Deposit.objects.filter(client=instance.client).first()
    TrackingMovement(
        envio=instance,
        user=instance.created_by,
        action=TrackingMovement.ACTION_ADDED_TO_SYSTEM,
        result=TrackingMovement.RESULT_ADDED_TO_SYSTEM,
        deposit=deposit
    ).save()


@receiver(post_save, sender=Envio, dispatch_uid="create_tracking_movement")
def create_tracking(sender, instance, **kwargs):
    base_create_tracking(instance)


class Bolson(models.Model):

    envios = models.ManyToManyField(Envio)
    datetime_created = models.DateTimeField(
        verbose_name="creation datetime", auto_now_add=True)
    carrier = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=False, null=False, default=None)
    history = HistoricalRecords()

    def count(self):
        return len(self.envios)

    def __str__(self):
        return f'{self.carrier.username} ({len(self.envios)} envíos)'

    class Meta:
        verbose_name = 'Bolsón'
        verbose_name_plural = 'Bolsones'


class Deposit(models.Model):

    town = models.ForeignKey(Town, null=True, on_delete=models.SET_NULL)
    name = models.CharField(verbose_name="name", max_length=50)
    is_ours = models.BooleanField(default=False)
    client = models.ForeignKey(
        Client, verbose_name='client',
        on_delete=models.CASCADE, blank=True, null=True)
    history = HistoricalRecords()

    def __str__(self):
        owner = 'Sinergia' if self.is_ours else self.client.name
        return f'{self.name} ({owner})'

    class Meta:
        verbose_name = 'Depósito'
        verbose_name_plural = 'Depósitos'


class TrackingMovement(models.Model):

    ACTION_ADDED_TO_SYSTEM = "AS"
    ACTION_RECOLECTION = "RC"
    ACTION_DEPOSIT = "DP"
    ACTION_DELIVERY_ATTEMPT = 'DA'
    ACTIONS = [
        (ACTION_ADDED_TO_SYSTEM, "Carga en sistema"),
        (ACTION_RECOLECTION, "Recolección"),
        (ACTION_DEPOSIT, "Depósito"),
        (ACTION_DELIVERY_ATTEMPT, "Intento de entrega"),
    ]

    RESULT_ADDED_TO_SYSTEM = '_new'
    RESULT_IN_DEPOSIT = 'in_deposit'
    RESULT_SUCCESSFUL_DELEIVERY = 'success'
    RESULT_REJECTED_AT_DESTINATION = 'rejected'
    RESULT_REPROGRAMED = 'reprogram'
    RESULT_NO_ANSWER = 'not-respond'
    RESULT_OTHER = 'custom'
    RESULTS = [
        (RESULT_ADDED_TO_SYSTEM, 'Agregado al sistema'),
        (RESULT_IN_DEPOSIT, 'En depósito'),
        (RESULT_SUCCESSFUL_DELEIVERY, 'Entrega exitosa'),
        (RESULT_REJECTED_AT_DESTINATION, 'Rechazado en lugar de destino'),
        (RESULT_REPROGRAMED, 'Reprogramado'),
        (RESULT_NO_ANSWER, 'Sin respuesta'),
        (RESULT_OTHER, 'Otro'),
    ]

    envio = models.ForeignKey(Envio,
                              verbose_name="Envio relacionado",
                              on_delete=models.CASCADE,
                              null=True, blank=False, default=None)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             null=True, on_delete=models.SET_NULL,
                             verbose_name="user responsible")
    action = models.CharField(verbose_name="movement action", max_length=50,
                              default=ACTION_ADDED_TO_SYSTEM,
                              blank=False, null=False, choices=ACTIONS)
    result = models.CharField(verbose_name="movement result", max_length=50,
                              default=RESULT_ADDED_TO_SYSTEM, blank=False,
                              null=False, choices=RESULTS)
    comment = models.TextField(verbose_name="comment", max_length=200,
                               default=None, blank=True, null=True)
    deposit = models.ForeignKey(
        Deposit, on_delete=models.SET_NULL,
        verbose_name="deposit", default=None, blank=True, null=True)
    date_time = models.DateTimeField(
        verbose_name="action's date time", auto_now_add=True)
    history = HistoricalRecords()

    def __str__(self):
        user = self.user.username
        dt = self.date_time.strftime('%Y-%m-%d_%H-%M')
        action = self.get_action_display()
        result = self.get_result_display()
        return f'{dt}_{user}_{action}_TO_{result}'

    class Meta:
        verbose_name = 'Movimiento'
        verbose_name_plural = 'Movimientos'


DETAIL_CODES = {
    "0": {'multiplier': 1, 'name': 'Paquete hasta 5k'},
    "1": {'multiplier': 1.3, 'name': 'Bulto hasta 10k'},
    "2": {'multiplier': 1.6, 'name': 'Bulto hasta 20k'},
    "3": {'multiplier': 2, 'name': 'Miniflete'},
    "4": {'multiplier': 3, 'name': 'Urgente'},
    "5": {'multiplier': 1.2, 'name': 'Trámite'},
}


class PriceCalculator(object):

    def __init__(self, envio: Envio):
        self.envio = envio
        self.discount = self.envio.client.discount
        return

    def calculate(self) -> Decimal:
        """Performs de calculation for the price of the 'envio'

        Returns:
            Decimal: The total price
        """
        # Get the 'envio'
        envio = self.envio

        # Get the town of recipient's address
        town = envio.recipient_town

        #  Get the code. If 'envio' is from flex, return flex's code for
        # given town, else the normal code.
        code = town.flex_code if envio.is_flex else town.delivery_code

        # Set code's price to default price. Later used when
        # parsing the detail to a price
        self.default_price = code.price

        # Get the total price
        total_price = self.get_price()

        # If the 'envio' has got a discount
        discount = envio.client.discount
        if discount and discount > 0:
            # Apply it to total price
            total_price = Decimal(total_price * (discount / 100))

        # return the total price
        return total_price

    def detail_to_price(self, detail) -> Decimal:
        """Parse a package detail pair in "3-4" format,
        where 3 is the id-code for the type of package,
        and 4 is the amount of packages.

        Args:
            detail (str): package detail pair in "3-4" format.

        Returns:
            Decimal: the total price.
        """
        parts = detail.split('-')
        code = parts[0]
        amount = parts[1]
        detail_code = DETAIL_CODES[code]
        total_price = Decimal(
            self.default_price * detail_code["multiplier"] * amount)
        return total_price

    def get_price(self):
        if not self.envio.is_flex:
            detail_codes = self.envio.detail.split(',')
            prices = map(self.detail_to_price, detail_codes)
            return Decimal(sum(prices))
        return Decimal(self.default_price)


class ListOfEnvios(object):

    def __init__(self, envios):

        pass


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
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        verbose_name="Usuario", blank=False, null=False)
    load_status = models.CharField(
        verbose_name="Estado",
        max_length=1, choices=LOADING_STATUSES,
        default=LOADING_STATUS_PROCESSING)
    client = models.ForeignKey(
        Client, on_delete=models.SET_NULL,
        verbose_name="Usuario", blank=True, null=True)
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
    history = HistoricalRecords()

    @property
    def short_errors_display(self):
        return truncatechars(self.errors, 100)

    @property
    def short_csv_result_display(self):
        return truncatechars(self.csv_result, 1000)

    class Meta:
        verbose_name = 'Carga masiva de envios'
        verbose_name_plural = 'Cargas masivas de envios'
