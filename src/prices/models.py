from django.db import models


class DeliveryCode(models.Model):

    code = models.CharField(
        verbose_name='code', max_length=5, blank=False, null=False)
    price = models.DecimalField(
        verbose_name="Price", max_digits=8, decimal_places=2)

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = 'Código de Mensajería'
        verbose_name_plural = 'Códigos de Mensajería'


class FlexCode(models.Model):

    code = models.CharField(
        verbose_name='code', max_length=5, blank=False, null=False)
    price = models.DecimalField(
        verbose_name="Price", max_digits=8, decimal_places=2)

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = 'Código de Flex'
        verbose_name_plural = 'Códigos de Flex'
