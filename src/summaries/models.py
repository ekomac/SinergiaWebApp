# Python
from datetime import timedelta
from datetime import datetime
import json
from decimal import Decimal
from typing import Any, Dict

# Django
from django.conf import settings
from django.db import models

# Project
from envios.models import Envio
from envios.utils import calculate_price, get_detail_readable


class Summary(models.Model):

    date_created = models.DateTimeField(
        auto_now_add=True, verbose_name='Fecha de creación',
        blank=False, null=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        verbose_name='Creado por', blank=False, null=False,
        related_name="autor")
    date_from = models.DateField(
        verbose_name='Desde', blank=False, null=False)
    date_to = models.DateField(
        verbose_name='Hasta', blank=False, null=False)
    last_calculated_total = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name='Último total calculado',
        blank=True, null=True)

    @property
    def envios_queried(self):
        return self.__get_envios()

    def __get_envios(self):
        return Envio.objects.filter(
            **self.get_envios_filters()).order_by('date_delivered')

    def get_envios_filters(self) -> Dict[str, Any]:
        raise NotImplementedError("This method should be overrided.")

    def total_cost(self) -> Decimal:
        total = Decimal(0)
        total = sum([calculate_price(envio) for envio in self.__get_envios()])
        return round(total)

    def total_envios(self) -> int:
        return self.__get_envios().count()

    def get_envios(self, date_as_str: bool = True) -> dict:
        result = []
        for envio in self.__get_envios():
            if envio.is_flex:
                code = envio.town.flex_code
                code_type = "Flex"
            else:
                code = envio.town.delivery_code
                code_type = "Mensajería"
            if date_as_str:
                date = envio.date_delivered.strftime("%d/%m/%Y")
            else:
                date = envio.date_delivered
            as_dict = {
                'id': envio.pk,
                'destination': envio.full_address,
                'price': str(calculate_price(envio)),
                'code': code.code,
                'code_type': code_type,
                'date_delivered': date,
                'detail': get_detail_readable(envio),
            }
            result.append(as_dict)
        return result

    def envios_as_JSON(self):
        return json.dumps(self.get_envios())


class ClientSummary(Summary):

    client = models.ForeignKey(
        'clients.Client', on_delete=models.CASCADE, verbose_name='Cliente',
        blank=True, null=True, related_name="client_summary")

    def get_envios_filters(self) -> Dict[str, Any]:
        offset_hours = settings.LOCAL_TIMEZONE_DIFFERENCE.get("hours")
        offset_minutes = settings.LOCAL_TIMEZONE_DIFFERENCE.get("minutes")
        _to = datetime(self.date_to.year, self.date_to.month,
                       self.date_to.day, offset_hours, offset_minutes, 0)
        next_day = _to + timedelta(days=1)
        _from = datetime(self.date_from.year, self.date_from.month,
                         self.date_from.day, offset_hours, offset_minutes, 0)
        return {
            'date_delivered__gte': _from,
            'date_delivered__lt': next_day,
            'status': Envio.STATUS_DELIVERED,
            'client': self.client,
        }

    @property
    def envios(self):
        return self.get_envios()

    def __str__(self):
        client = self.client.name
        dfrom = self.date_from.strftime("%d/%m/%Y")
        tfrom = self.date_to.strftime("%d/%m/%Y")
        return "Resumen de cuenta de %s del %s al %s" % (client, dfrom, tfrom)

    class Meta:
        verbose_name = 'Resumen de cliente'
        verbose_name_plural = 'Resúmenes de clientes'
        ordering = ['-date_created']


class EmployeeSummary(Summary):

    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        verbose_name='Empleado', blank=True, null=True,
        related_name="employee_summary")

    def get_envios_filters(self) -> Dict[str, Any]:
        offset_hours = settings.LOCAL_TIMEZONE_DIFFERENCE.get("hours")
        offset_minutes = settings.LOCAL_TIMEZONE_DIFFERENCE.get("minutes")
        _to = datetime(self.date_to.year, self.date_to.month,
                       self.date_to.day, offset_hours, offset_minutes, 0)
        next_day = _to + timedelta(days=1)
        _from = datetime(self.date_from.year, self.date_from.month,
                         self.date_from.day, offset_hours, offset_minutes, 0)
        return {
            'date_delivered__gte': _from,
            'date_delivered__lt': next_day,
            'status': Envio.STATUS_DELIVERED,
            'deliverer': self.employee,
        }

    def __str__(self):
        employee = self.employee.full_name_formal
        dfrom = self.date_from.strftime("%d/%m/%Y")
        tfrom = self.date_to.strftime("%d/%m/%Y")
        return "Resumen de cuenta de %s del %s al %s" % (
            employee, dfrom, tfrom)

    class Meta:
        verbose_name = 'Resumen de empleado'
        verbose_name_plural = 'Resúmenes de empleados'
        ordering = ['-date_created']
