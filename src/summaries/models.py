from decimal import Decimal
from typing import Any, Dict
from django.conf import settings
from django.db import models

from envios.models import Envio


class Summary(models.Model):

    date_created = models.DateTimeField(
        auto_now_add=True, verbose_name='Fecha de creación',
        blank=False, null=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        verbose_name='Creado por', blank=False, null=False,
        related_name="autor",)
    date_from = models.DateField(
        verbose_name='Desde', blank=False, null=False)
    date_to = models.DateField(
        verbose_name='Hasta', blank=False, null=False)
    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE,
                               verbose_name='Cliente', blank=True, null=True)
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        verbose_name='Empleado', blank=True, null=True,
        related_name="empleado")
    last_calculated_total = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name='Último total calculado',
        blank=True, null=True)

    def __str__(self):
        if self.client:
            return f'Factura {self.pk}: {self.client} del'\
                + f' {self.date_from:%Y-%m-%d} al {self.date_to:%Y-%m-%d}'
        else:
            return f'Liquidación {self.pk}: {self.employee.full_name_formal} '\
                + f'del {self.date_from:%Y-%m-%d} al {self.date_to:%Y-%m-%d}'

    def __get_envios(self):
        return Envio.objects.filter(**self.__get_envios_filters())

    def __get_envios_filters(self) -> Dict[str, Any]:
        filters = {
            'date_delivered__gte': self.date_from,
            'date_delivered__lte': self.date_to,
            'status': Envio.STATUS_DELIVERED,
        }
        if self.client:
            filters['client'] = self.client
        if self.employee:
            filters['carrier'] = self.employee
        return filters

    @property
    def total_cost(self) -> Decimal:
        total = Decimal(0)
        total = sum([envio.price for envio in self.__get_envios()])
        return round(total)

    @property
    def envios_dict(self) -> dict:
        result_dict = {}
        for envio in self.__get_envios():
            if envio.is_flex:
                code = envio.town.flex_code
            else:
                code = envio.town.delivery_code
            result_dict[envio.pk] = {
                'destination': envio.full_address,
                'price': envio.price,
                'code': code,
                'date_delivered': envio.date_delivered,
                'detail': envio.readable_detail,
            }
        return result_dict

    class Meta:
        verbose_name = 'Resumen'
        verbose_name_plural = 'Resúmenes'
        ordering = ['-date_created']
