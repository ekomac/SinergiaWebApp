from django.db import models
from django.conf import settings


class DeliveryCode(models.Model):

    code = models.CharField(
        verbose_name='code', max_length=5, blank=False,
        null=False, unique=True)
    price = models.DecimalField(
        verbose_name="Price", max_digits=8, decimal_places=2)
    last_update = models.DateTimeField(
        verbose_name="Última actualización", auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        verbose_name="Actualizado por", blank=True, null=True, default=None)

    def __str__(self):
        return f'{self.code} a ${self.price}'

    class Meta:
        verbose_name = 'Código de Mensajería'
        verbose_name_plural = 'Códigos de Mensajería'
        ordering = ['code']


class FlexCode(models.Model):

    code = models.CharField(
        verbose_name='Código', max_length=5, blank=False,
        null=False, unique=True)
    price = models.DecimalField(
        verbose_name="Price", max_digits=8, decimal_places=2)
    last_update = models.DateTimeField(
        verbose_name="Última actualización", auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        verbose_name="Actualizado por", blank=True, null=True, default=None)

    def __str__(self):
        return f'{self.code} a ${self.price}'

    class Meta:
        verbose_name = 'Código de Flex'
        verbose_name_plural = 'Códigos de Flex'
        ordering = ['code']
