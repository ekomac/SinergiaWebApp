from django.db import models
from simple_history.models import HistoricalRecords


class Client(models.Model):

    name = models.CharField(verbose_name="client name",
                            max_length=50)
    contact_name = models.CharField(
        verbose_name="Persona de contacto",
        max_length=50, blank=True, null=True)
    contact_phone = models.CharField(
        verbose_name="Número de teléfono",
        max_length=50, blank=True, null=True)
    contact_email = models.CharField(
        verbose_name="Email", max_length=50, blank=True, null=True)
    discount = models.IntegerField(default=0, blank=False, null=False)
    history = HistoricalRecords()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
