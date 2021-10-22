from django.db import models
from django.conf import settings
from simple_history.models import HistoricalRecords
from account.models import Account


class Zone(models.Model):

    name = models.CharField(
        verbose_name='Name', max_length=50, blank=False,
        null=False, unique=True)
    asigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True,
        blank=True, default=None, on_delete=models.SET_NULL,
        related_name='asignet_to')
    last_update = models.DateTimeField(
        verbose_name="Última actualización", auto_now=True)
    updated_by = models.ForeignKey(
        Account, on_delete=models.SET_NULL,
        verbose_name="Actualizado por", blank=True, null=True, default=None,
        related_name='updated_by')
    history = HistoricalRecords()

    def __str__(self):
        return self.name.title()

    class Meta:
        verbose_name = "Zona"
        verbose_name_plural = "Zonas"


class Partido(models.Model):

    PROVINCES = [
        ('BA', 'Buenos Aires'),
        ('CAB', 'CABA'),
        ('CA', 'Catamarca'),
        ('CH', 'Chaco'),
        ('CT', 'Chubut'),
        ('CR', 'Corrientes'),
        ('CB', 'Córdoba'),
        ('ER', 'Entre Ríos'),
        ('FO', 'Formosa'),
        ('JY', 'Jujuy'),
        ('LP', 'La Pampa'),
        ('LR', 'La Rioja'),
        ('MZ', 'Mendoza'),
        ('MI', 'Misiones'),
        ('NQN', 'Neuquén'),
        ('RN', 'Río Negro'),
        ('SA', 'Salta'),
        ('SJ', 'San Juan'),
        ('SL', 'San Luis'),
        ('SC', 'Santa Cruz'),
        ('SF', 'Santa Fe'),
        ('SE', 'Santiago del Estero'),
        ('TF', 'Tierra del Fuego...'),
        ('TU', 'Tucumán'),
    ]

    name = models.CharField(
        verbose_name='Name', max_length=50, blank=False, null=False)
    province = models.CharField(
        verbose_name='Province', max_length=3,
        choices=PROVINCES, blank=False, null=False, default='BA')
    zone = models.ForeignKey(
        Zone, blank=True, null=True, on_delete=models.SET_NULL)
    is_amba = models.BooleanField(default=False, blank=False, null=False)
    last_update = models.DateTimeField(
        verbose_name="Última actualización", auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        verbose_name="Actualizado por", blank=True, null=True, default=None)
    history = HistoricalRecords()

    def __str__(self):
        return self.name.title()

    class Meta:
        verbose_name = 'Partido'
        verbose_name_plural = 'Partidos'


class Town(models.Model):

    name = models.CharField(
        verbose_name='Name', max_length=70, blank=False, null=False)
    partido = models.ForeignKey(
        Partido, verbose_name='Partido',
        on_delete=models.CASCADE, blank=False, null=False)
    delivery_code = models.ForeignKey(
        'prices.DeliveryCode', verbose_name="Delivery code",
        blank=True, null=True, on_delete=models.SET_NULL)
    flex_code = models.ForeignKey(
        'prices.FlexCode', verbose_name="Flex code",
        blank=True, null=True, on_delete=models.SET_NULL)
    last_update = models.DateTimeField(
        verbose_name="Última actualización", auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        verbose_name="Actualizado por", blank=True, null=True, default=None)
    history = HistoricalRecords()

    def __str__(self):
        return self.name.title()

    class Meta:
        verbose_name = 'Localidad'
        verbose_name_plural = 'Localidades'


class ZipCode(models.Model):
    date_created = models.DateTimeField(
        verbose_name="Fecha de creación", auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        verbose_name="Usuario", blank=True, null=True)
    code = models.CharField(
        verbose_name="Numero", max_length=10,
        default=None, blank=False, null=False)
    towns = models.ManyToManyField(Town)
