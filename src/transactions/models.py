from django.conf import settings
from django.db import models


def proof_of_payment_upload_location(instance, filename):
    date = instance.date_created.strftime('%Y-%m-%d_%H-%M-%S')
    file_path = 'transactions/{id}/{date}-{filename}'.format(
        id=str(instance.id), date=date, filename=filename)
    return file_path


class Transaction(models.Model):

    date_created = models.DateTimeField(
        auto_now_add=True, verbose_name='Fecha de creación',
        blank=False, null=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        verbose_name='Creado por', blank=False, null=False)
    ammount = models.DecimalField(
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

    def __str__(self):
        return f'Transacción {self.pk}: {self.ammount} {self.description}'

    class Meta:
        verbose_name = 'Transacción'
        verbose_name_plural = 'Transacciones'
        ordering = ['-date_created']
