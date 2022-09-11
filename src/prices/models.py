from django.db import models
from django.conf import settings


class DeliveryCode(models.Model):

    code = models.CharField(
        verbose_name='code', max_length=100, blank=False,
        null=False, unique=True)
    price = models.DecimalField(
        verbose_name="Price", max_digits=20, decimal_places=2)
    max_5k_price = models.DecimalField(
        verbose_name="Precio hasta 5kg", max_digits=20, decimal_places=2)
    bulto_max_10k_price = models.DecimalField(
        verbose_name="Precio Bulto hasta 10kg",
        max_digits=20, decimal_places=2)
    bulto_max_20k_price = models.DecimalField(
        verbose_name="Precio Bulto hasta 20kg",
        max_digits=20, decimal_places=2)
    miniflete_price = models.DecimalField(
        verbose_name="Precio miniflete",
        max_digits=20, decimal_places=2)
    tramite_price = models.DecimalField(
        verbose_name="Precio trámite",
        max_digits=20, decimal_places=2)
    camioneta_price = models.DecimalField(
        verbose_name="Precio camioneta",
        max_digits=20, decimal_places=2)
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
        verbose_name='Código', max_length=100, blank=False,
        null=False, unique=True)
    price = models.DecimalField(
        verbose_name="Price", max_digits=20, decimal_places=2)
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
