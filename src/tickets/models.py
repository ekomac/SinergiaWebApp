from django.conf import settings
from django.db import models
from simple_history.models import HistoricalRecords


class Ticket(models.Model):

    PRIORITY_CHOICES = (
        ('1', 'Alta'),
        ('2', 'Media'),
        ('3', 'Baja'),
    )

    STATUS_CHOICES = (
        ('1', 'Enviado'),
        ('2', 'Abierto'),
        ('3', 'Cerrado'),
    )

    CLOSED_REASONS = (
        ('1', 'Cancelado'),
        ('2', 'Irrelevante'),
        ('3', 'Innecesario'),
        ('4', 'Resuelto'),
        ('5', 'Existe otro ticket similar'),
        ('6', 'No se pudo resolver'),
    )

    date_created = models.DateTimeField(
        auto_now_add=True, verbose_name="Creación")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Autor",
        blank=True, null=True, default=None)
    priority = models.CharField(
        max_length=1, choices=PRIORITY_CHOICES, default='2',
        blank=False, null=False, verbose_name="Prioridad")
    subject = models.CharField(
        max_length=100, blank=False, null=False, verbose_name="Asunto")
    msg = models.TextField(blank=False, null=False, verbose_name="Mensaje")
    status = models.CharField(
        max_length=1, choices=STATUS_CHOICES, default='1',
        blank=False, null=False, verbose_name="Estado")
    closed_reason = models.CharField(
        max_length=1, choices=CLOSED_REASONS, default='6',
        blank=True, null=True, verbose_name="Razón de cierre")
    closed_msg = models.TextField(
        blank=True, null=True, verbose_name="Mensaje de cierre")
    history = HistoricalRecords()
