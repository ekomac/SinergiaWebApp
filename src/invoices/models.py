from django.conf import settings
from django.db import models


class Invoice(models.Model):

    date_created = models.DateTimeField(
        auto_now_add=True, verbose_name='Fecha de creación',
        blank=False, null=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        verbose_name='Creado por', blank=False, null=False)
    date_from = models.DateField(
        verbose_name='Desde', blank=False, null=False)
    date_to = models.DateField(
        verbose_name='Hasta', blank=False, null=False)
    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE,
                               verbose_name='Cliente', blank=False, null=False)
    envios = models.ManyToManyField(
        'envios.Envio', verbose_name='Envios', blank=False, null=False)
    last_calculated_total = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name='Último total calculado',
        blank=True, null=True)
    charged = models.BooleanField(
        verbose_name='¿Cobrado?', blank=False, null=False, default=False)

    def __str__(self):
        return f'Factura {self.pk}: {self.client} del'\
            + f' {self.date_from:%Y-%m-%d} al {self.date_to:%Y-%m-%d}'
