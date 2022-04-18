from django.dispatch import receiver
from django.db.models.signals import post_delete
from decimal import Decimal
from django.conf import settings
from django.db import models

from utils.views import truncate_start


def proof_of_payment_upload_location(instance, filename):
    date = instance.date_created.strftime('%Y-%m-%d_%H-%M-%S')
    file_path = 'transactions/{id}/{date}-{filename}'.format(
        id=str(instance.id), date=date, filename=filename)
    return file_path


class Transaction(models.Model):

    CATEGORIES = (
        ('0', 'Administrativo'),
        ('1', 'Alquiler'),
        ('12', 'Cobro por cuenta y orden de terceros'),
        ('2', 'Compras'),
        ('3', 'Facturacion'),
        ('4', 'Impuestos'),
        ('5', 'Insumos'),
        ('6', 'Mantenimiento'),
        ('14', 'Pagos'),
        ('7', 'Publicidad'),
        ('13', 'Retiros de caja en efectivo'),
        ('8', 'Seguros'),
        ('9', 'Servicios'),
        ('10', 'Sueldos'),
        ('11', 'Otros'),
    )

    date_created = models.DateTimeField(
        auto_now_add=True, verbose_name='Fecha de creación',
        blank=False, null=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        verbose_name='Creado por', blank=False, null=False)
    date = models.DateField(
        verbose_name='Fecha', blank=False, null=False)
    category = models.CharField(
        max_length=2, choices=CATEGORIES,
        verbose_name='Categoría', blank=False, null=False)
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name='Monto',
        blank=False, null=False)
    description = models.CharField(
        verbose_name='Descripción', blank=False, null=False, max_length=100)
    summary = models.ForeignKey(
        'summaries.Summary', on_delete=models.CASCADE,
        verbose_name='Resumen', blank=True, null=True)
    transaction_number = models.CharField(
        verbose_name='Número de transacción', blank=True, null=True,
        max_length=200)
    proof_of_payment = models.FileField(
        upload_to=proof_of_payment_upload_location,
        verbose_name='Comprobante de pago', blank=True, null=True)
    hash_sum = models.CharField(max_length=108, blank=True, null=True)

    def __str__(self):
        return f'Transacción {self.pk}: {self.amount} {self.description}'

    @property
    def sign(self):
        return '+' if Decimal(str(self.amount)) >= Decimal(0) else '-'

    @property
    def trucated_proof_url(self):
        if self.proof_of_payment:
            return truncate_start(self.proof_of_payment.url, 30)
        return False

    class Meta:
        verbose_name = 'Transacción'
        verbose_name_plural = 'Transacciones'
        ordering = ['-date_created']


@receiver(post_delete, sender=Transaction)
def submission_delete(sender, instance, **kwargs):
    instance.proof_of_payment.delete(False)
