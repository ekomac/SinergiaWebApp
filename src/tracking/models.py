from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from simple_history.models import HistoricalRecords

from deposit.models import Deposit


def upload_location(instance, filename):
    date = instance.date_created.strftime('%Y-%m-%d')
    file_path = 'movements/{movement_id}-{date}-{filename}'.format(
        movement_id=instance.pk, date=date, filename=filename)
    return file_path


class TrackingMovement(models.Model):

    ACTION_ADDED_TO_SYSTEM = "AS"
    ACTION_RECOLECTION = "RC"
    ACTION_DEPOSIT = "DP"
    ACTION_DELIVERY_ATTEMPT = 'DA'
    ACTION_TRANSFER = 'TR'
    ACTIONS = [
        (ACTION_ADDED_TO_SYSTEM, "Carga en sistema"),
        (ACTION_RECOLECTION, "Recolección"),
        (ACTION_DEPOSIT, "Depósito"),
        (ACTION_DELIVERY_ATTEMPT, "Intento de entrega"),
    ]

    RESULT_ADDED_TO_SYSTEM = '_new'
    RESULT_TRANSFERED = 'transfered'
    RESULT_IN_DEPOSIT = 'in_deposit'
    RESULT_DELIVERED = 'success'
    RESULT_REJECTED_AT_DESTINATION = 'rejected'
    RESULT_REPROGRAMED = 'reprogram'
    RESULT_NO_ANSWER = 'not-respond'
    RESULT_OTHER = 'custom'
    RESULTS = [
        (RESULT_ADDED_TO_SYSTEM, 'Agregado al sistema'),
        (RESULT_IN_DEPOSIT, 'En depósito'),
        (RESULT_DELIVERED, 'Entrega exitosa'),
        (RESULT_REJECTED_AT_DESTINATION, 'Rechazado en lugar de destino'),
        (RESULT_REPROGRAMED, 'Reprogramado'),
        (RESULT_NO_ANSWER, 'Sin respuesta'),
        (RESULT_TRANSFERED, 'Transferido'),
        (RESULT_OTHER, 'Otro'),
    ]

    envios = models.ManyToManyField(
        'envios.Envio', verbose_name="Envios relacionados")
    created_by = models.ForeignKey('account.Account',
                                   related_name='movement_created_by',
                                   null=True, on_delete=models.SET_NULL,
                                   verbose_name="author")
    carrier = models.ForeignKey('account.Account',
                                related_name='movement_carrier', blank=True,
                                null=True, on_delete=models.SET_NULL,
                                verbose_name="user carrying package")
    action = models.CharField(verbose_name="Acción", max_length=50,
                              default=ACTION_ADDED_TO_SYSTEM,
                              blank=False, null=False, choices=ACTIONS)
    result = models.CharField(verbose_name="Resultado", max_length=50,
                              default=RESULT_ADDED_TO_SYSTEM, blank=False,
                              null=False, choices=RESULTS)
    comment = models.TextField(verbose_name="Comentario", max_length=200,
                               default=None, blank=True, null=True)
    deposit = models.ForeignKey(
        Deposit, on_delete=models.SET_NULL,
        verbose_name="deposit", default=None, blank=True, null=True)
    date_created = models.DateTimeField(
        verbose_name="action's date time",
        auto_now_add=True,
        null=False,
        blank=False)
    proof = models.FileField(upload_to=upload_location,
                             verbose_name="archivo probatorio",
                             blank=True, null=True)
    history = HistoricalRecords()

    def __str__(self):
        user = self.created_by.username if self.created_by else ""
        dt = ""
        if self.date_created:
            dt = self.date_created.strftime('%Y-%m-%d_%H-%M')
        action = self.get_action_display()
        result = self.get_result_display()
        return f'{dt}_{user}_{action}_to_{result}'

    def admin_display(self):
        added = self.action == self.ACTION_ADDED_TO_SYSTEM \
            and self.result == self.RESULT_ADDED_TO_SYSTEM
        withdraw_from_origin = self.action == self.ACTION_RECOLECTION \
            and self.result == self.RESULT_TRANSFERED \
            and self.deposit.client is not None
        deposit = self.action == self.ACTION_DEPOSIT \
            and self.result == self.RESULT_IN_DEPOSIT \
            and self.deposit.client is None
        withdraw_from_central = self.action == self.ACTION_RECOLECTION \
            and self.result == self.RESULT_TRANSFERED \
            and self.deposit.client is None
        withdraw_from_deposit = self.action == self.ACTION_RECOLECTION \
            and self.result == self.RESULT_TRANSFERED \
            and self.deposit.client is None
        delivered = self.action == self.ACTION_DELIVERY_ATTEMPT \
            and self.result == self.RESULT_DELIVERED

        if added:
            return '<b>Nuevo</b>: Agregado al sistema.'
        elif withdraw_from_origin:
            return '<b>Ingreso</b>: Retirado del depósito de origen.'
        elif deposit:
            return '<b>En depósito</b>: El envío ingreso en nuestro ' +\
                f'depósito {self.deposi} y está listo para su distribución.'
        elif withdraw_from_central:
            return '<b>Salida de depósito</b>: El envío entró en el ' +\
                'circuito de distribución.'
        elif withdraw_from_deposit:
            return '<b>En depósito</b>: El envío está camino al' +\
                'domicilio del desinatario.'
        elif delivered:
            return '<b>Entregado</b>: El envío se entregó con éxito.'

        return self.__str__()

    def end_user_display(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Movimiento'
        verbose_name_plural = 'Movimientos'


@ receiver(post_delete, sender=TrackingMovement)
def submission_delete(sender, instance, **kwargs):
    instance.proof.delete(False)
