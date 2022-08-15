# django
from django.conf import settings
from django.db import models


# project
from clients.models import Client
from places.models import Town


class Deposit(models.Model):
    date_created = models.DateTimeField(
        verbose_name="Fecha de creación", auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        verbose_name="Usuario", blank=True, null=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE,
                               verbose_name="Cliente", blank=True, null=True)
    name = models.CharField(
        verbose_name="Nombre", max_length=50,
        default=None, blank=False, null=False,
        unique=True)
    address = models.CharField(
        verbose_name="Dirección", max_length=100,
        default=None, blank=False, null=False)
    zip_code = models.CharField(
        verbose_name="Código postal", max_length=10,
        blank=True, null=True)
    town = models.ForeignKey(
        Town, verbose_name="Localidad",
        on_delete=models.CASCADE, blank=False, null=False)
    phone = models.CharField(
        verbose_name="Teléfono", max_length=20,
        default=None, blank=True, null=True)
    email = models.EmailField(
        verbose_name="Email", max_length=50,
        default=None, blank=True, null=True)
    is_active = models.BooleanField(
        verbose_name="Activo?", default=True, blank=False, null=False)
    is_sinergia = models.BooleanField(
        verbose_name="Es de sinergia?", default=False, blank=False, null=False)
    is_central = models.BooleanField(
        verbose_name="Es central?", default=False, blank=False, null=False)

    def __str__(self):
        name = self.name
        client = f'{self.client.name}' if self.client else "Sinergia"
        address = '{title},{zip_code} {town}'.format(
            title=self.address.title(),
            zip_code=" %s" % self.zip_code if self.zip_code else "",
            town=self.town
        )
        return f'{name} en {address} de {client}'

    def full_name(self):
        return self.__str__()

    def full_address(self):
        return f'{self.address.title()}, {self.zip_code} {self.town}'

    class Meta:
        verbose_name = 'Depósito'
        verbose_name_plural = 'Depósitos'
        ordering = ['name']
