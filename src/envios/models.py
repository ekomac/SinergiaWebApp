from django.db import models
from account.models import Account
from clients import Client
from places import Town


class Envio(models.Model):

    STATUSES = [
        ('N', 'Nuevo'),
        ('V', 'Viajando'),
        ('E', 'Entregado'),
        (),
    ]

    SCHEDULES = [
        ('07-10', '7 a 10 h'),
        ('10-13', '10 a 13 h'),
        ('13-16', '13 a 16 h'),
        ('16+', '+16 h'),
    ]

    date_created = models.DateTimeField(
        verbose_name="date joined", auto_now_add=True)
    register = models.ForeignKey(
        Account, on_delete=models.CASCADE, verbose_name="user",
        blank=False, null=False)
    status = models.CharField(verbose_name="status",
                              max_length=2, choices=STATUSES)
    detail = models.CharField(verbose_name="datail",
                              max_length=2000, default='0-1')
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, verbose_name="client",
        blank=False, null=False)
    recipient_name = models.CharField(
        verbose_name="recipient's name", max_length=50,
        blank=True, null=True)
    recipient_doc = models.CharField(
        verbose_name="recipient's doc id", max_length=50,
        blank=True, null=True)
    recipient_doc = models.CharField(
        verbose_name="recipient's doc id", max_length=50,
        blank=True, null=True)
    recipient_address = models.CharField(
        verbose_name="recipient's addresse", max_length=100,
        blank=False, null=False)
    recipient_entrances = models.CharField(
        verbose_name="recipient's entrances", max_length=100,
        blank=True, null=True)
    recipient_city = models.ForeignKey(
        Town, on_delete=models.CASCADE,
        verbose_name="recipient's city", blank=False, null=False)
    recipient_zipcode = models.CharField(
        verbose_name="recipient's zip code", max_length=10,
        blank=True, null=True)
    recipient_charge = models.DecimalField(
        verbose_name="recipient's charge",
        decimal_places=2, max_digits=40, blank=True, null=True)
    max_delivery_date = models.DateField(
        verbose_name="max delivery date", blank=True, null=True)
    flex_id = models.CharField(
        verbose_name="flex id", max_length=50,
        blank=True, null=True)
    delivery_schedule = models.CharField(
        verbose_name='delivery schedule', choices=SCHEDULES,
        blank=True, null=True)

    def __str__(self):
        address = self.recipient_address
        city = self.recipient_city.name
        client = self.client
        return f'{address}, {city} from {client}'


class Bolson(models.Model):

    envios = models.ManyToManyField(Envio, blank=True, null=True)


class TrackingMovement(models.Model):

    envios = models.ManyToManyField(Envio, blank=True, null=True)
    bolsones = models.ManyToManyField(Bolson, blank=True, null=True)
