from django.db.models.signals import post_delete, post_save
from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.template.defaultfilters import truncatechars
from clients.models import Client
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
    floor_apartment = models.CharField(
        verbose_name="Piso/Departamento", max_length=50, blank=True,
        null=True)
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
        zipcode = f"{self.zipcode} " if self.zipcode is not None else ""
        return f'{self.street}, {zipcode}{self.town}'


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
        if not self.name:
            return "No especificado"
        if not self.doc:
            return f'{self.name}'
        else:
            return f'{self.name} ({self.doc})'


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
    STATUS_RETURNED = 'R'
    STATUS_RETURNED_TEXT = 'Devuelto'
    STATUS_CANCELED = 'C'
    STATUS_CANCELED_TEXT = 'Cancelado'

    SCHEDULE_INDEX_7_10 = '07-10'
    SCHEDULE_PHRASE_7_10 = '7 a 10 h'
    SCHEDULE_INDEX_10_13 = '10-13'
    SCHEDULE_PHRASE_10_13 = '10 a 13 h'
    SCHEDULE_INDEX_13_16 = '13-16'
    SCHEDULE_PHRASE_13_16 = '13 a 16 h'
    SCHEDULE_INDEX_16_ON = '16+'
    SCHEDULE_PHRASE_16_ON = '+16 h'

    STATUSES = (
        (STATUS_NEW, STATUS_NEW_TEXT),
        (STATUS_MOVING, STATUS_MOVING_TEXT),
        (STATUS_STILL, STATUS_STILL_TEXT),
        (STATUS_DELIVERED, STATUS_DELIVERED_TEXT),
        (STATUS_RETURNED, STATUS_RETURNED_TEXT),
        (STATUS_CANCELED, STATUS_CANCELED_TEXT),
    )

    ALL_STATUSES = [x for x, _ in STATUSES]

    ON_CIRCUIT_STATUSES = (STATUS_NEW,
                           STATUS_MOVING,
                           STATUS_STILL,
                           STATUS_RETURNED)

    SCHEDULES = (
        (SCHEDULE_INDEX_7_10, SCHEDULE_PHRASE_7_10),
        (SCHEDULE_INDEX_10_13, SCHEDULE_PHRASE_10_13),
        (SCHEDULE_INDEX_13_16, SCHEDULE_PHRASE_13_16),
        (SCHEDULE_INDEX_16_ON, SCHEDULE_PHRASE_16_ON),
    )

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
        verbose_name="ID de Flex", max_length=50,
        blank=True, null=True)
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
    tracking_id = models.CharField(
        verbose_name="Tracking ID", blank=True, null=True,
        default=None, max_length=50, unique=True)
    receiver_doc = models.CharField(
        verbose_name="DNI del destinatario", max_length=20,
        blank=True, null=True)
    has_delivery_attempt = models.BooleanField(
        verbose_name="Se ha intentado entregar", default=False)

    def __str__(self):
        address = self.full_address
        client = self.client
        status = self.get_status_display()
        if status == self.STATUS_DELIVERED:
            return f'{address} ({status}) de {client}'
        where = ''
        if self.carrier is not None:
            where = ' @%s' % self.carrier
        elif self.deposit is not None:
            where = ' @%s' % self.deposit.name
        return f'{address} de {client} ({status}){where}'

    @property
    def destination_for_client(self):
        return self.full_address + ' de ' + self.client.name

    def get_status(self):
        status = self.get_status_display()
        carrier = self.carrier
        deposit = self.deposit
        if self.status in [self.STATUS_NEW, self.STATUS_STILL]:
            if deposit is not None:
                return f'{status}: {deposit}'
        if self.status == self.STATUS_MOVING and carrier is not None:
            return f'{status} con @{carrier.username}' +\
                f' ({carrier.first_name} {carrier.last_name})'
        return status

    class Meta:
        verbose_name = 'Envío'
        verbose_name_plural = 'Envíos'
        ordering = ['-date_created']


@receiver(post_save, sender=Envio)
def create_tracking_id(sender, instance, created, **kwargs):
    if created:
        if instance.tracking_id is None:
            if instance.is_flex and instance.flex_id is not None:
                instance.tracking_id = "ML%s" % instance.flex_id
            else:
                instance.tracking_id = "SN%s" % instance.pk
        instance.save()
    else:
        if instance.is_flex and instance.flex_id is not None:
            tracking_id = "ML%s" % instance.flex_id
        else:
            tracking_id = "SN%s" % instance.pk
        Envio.objects.filter(pk=instance.pk).update(
            tracking_id=tracking_id)


def bulk_file_upload_path(instance, filename):
    author_id = str(instance.created_by.id)
    date = instance.date_created.strftime('%Y%m%d')
    dirs = f'bulk_loads/{author_id}/'
    file_data = f'{date}_{filename}'
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
    unused_flex_ids = models.TextField(
        verbose_name="IDs de Flex no usados",
        blank=True, null=True, default=None)
    original_file = models.FileField(
        verbose_name="Archivo original",
        upload_to=bulk_file_upload_path,
        blank=True, null=True)

    @property
    def short_errors_display(self):
        return truncatechars(self.errors, 100)

    @property
    def short_csv_result_display(self):
        return truncatechars(self.csv_result, 1000)

    class Meta:
        verbose_name = 'Carga masiva de envios'
        verbose_name_plural = 'Cargas masivas de envios'


@receiver(post_delete, sender=BulkLoadEnvios)
def submission_delete(sender, instance, **kwargs):
    instance.original_file.delete(False)
