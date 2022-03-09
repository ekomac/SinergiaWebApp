from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from deposit.models import Deposit


def upload_location(instance, filename):
    date = instance.date_created.strftime('%Y-%m-%d')
    file_path = 'movements/{movement_id}-{date}-{filename}'.format(
        movement_id=instance.pk, date=date, filename=filename)
    return file_path


class TrackingMovement(models.Model):

    ACTION_ADDED_TO_SYSTEM = "AS"
    ACTION_COLLECTION = "RC"
    ACTION_DEPOSIT = "DP"
    ACTION_DELIVERY_ATTEMPT = 'DA'
    ACTION_TRANSFER = 'TR'
    ACTION_RETURN = "RE"
    ACTIONS = [
        (ACTION_ADDED_TO_SYSTEM, "Carga en sistema"),
        (ACTION_COLLECTION, "Recolección"),
        (ACTION_DEPOSIT, "Depósito"),
        (ACTION_DELIVERY_ATTEMPT, "Intento de entrega"),
        (ACTION_TRANSFER, "Transferencia"),
        (ACTION_RETURN, "Devolución"),
    ]

    RESULT_ADDED_TO_SYSTEM = '_new'
    RESULT_COLLECTED = 'collected'
    RESULT_TRANSFERED = 'transfered'
    RESULT_IN_DEPOSIT = 'in_deposit'
    RESULT_DELIVERED = 'success'
    RESULT_REJECTED_AT_DESTINATION = 'rejected'
    RESULT_REPROGRAMED = 'reprogram'
    RESULT_NO_ANSWER = 'not-respond'
    RESULT_OTHER = 'custom'
    RESULT_RETURNED = "returned"
    RESULTS = [
        (RESULT_ADDED_TO_SYSTEM, 'Agregado al sistema'),
        (RESULT_IN_DEPOSIT, 'En depósito'),
        (RESULT_DELIVERED, 'Entrega exitosa'),
        (RESULT_REJECTED_AT_DESTINATION, 'Rechazado en lugar de destino'),
        (RESULT_REPROGRAMED, 'Reprogramado'),
        (RESULT_NO_ANSWER, 'Sin respuesta'),
        (RESULT_TRANSFERED, 'Transferido'),
        (RESULT_COLLECTED, 'Recolectado'),
        (RESULT_OTHER, 'Otro'),
        (RESULT_RETURNED, 'Devuelto'),
    ]

    LABEL_ALL = 'all'
    LABEL_BY_ENVIOS_IDS = 'by_envios_ids'
    LABEL_BY_TOWNS_IDS = 'by_towns_ids'
    LABEL_BY_PARTIDOS_IDS = 'by_partidos_ids'
    LABEL_BY_ZONES_IDS = 'by_zones_ids'
    LABEL = [
        (LABEL_ALL, 'Todos'),
        (LABEL_BY_ENVIOS_IDS, 'por envíos'),
        (LABEL_BY_TOWNS_IDS, 'por localidades'),
        (LABEL_BY_PARTIDOS_IDS, 'por partidos'),
        (LABEL_BY_ZONES_IDS, 'por zonas'),
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
    label = models.CharField(verbose_name="Label", max_length=15,
                             choices=LABEL, default=LABEL_ALL,
                             blank=True, null=True)
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

    from_carrier = models.ForeignKey(
        'account.Account',
        related_name='movement_from_carrier',
        null=True, on_delete=models.SET_NULL,
        verbose_name="El usuario que transportó el/los paquete/s (FROM)")
    to_carrier = models.ForeignKey(
        'account.Account',
        related_name='movement_to_carrier',
        null=True, on_delete=models.SET_NULL,
        verbose_name="El usuario que tiene el/los paquete/s (TO)")
    from_deposit = models.ForeignKey(
        'deposit.Deposit',
        related_name='movement_from_deposit',
        null=True, on_delete=models.SET_NULL,
        verbose_name="El depósito que tenía el/los paquete/s (FROM)")
    to_deposit = models.ForeignKey(
        'deposit.Deposit',
        related_name='movement_to_deposit',
        null=True, on_delete=models.SET_NULL,
        verbose_name="El depósito que tiene el/los paquete/s (TO)")

    receiver_doc_id = models.CharField(
        verbose_name="Documento de quien recibió", max_length=12,
        blank=True, null=True)

    def __str__(self):
        user = self.created_by.username if self.created_by else ""
        dt = ""
        if self.date_created:
            dt = self.date_created.strftime('%Y-%m-%d_%H-%M')
        action = self.get_action_display()
        result = self.get_result_display()
        return f'{dt}_{user}_{action}_to_{result}'

    def admin_display(self):
        added = (self.action == self.ACTION_ADDED_TO_SYSTEM and
                 self.result == self.RESULT_ADDED_TO_SYSTEM)
        withdraw_from_origin = (self.action == self.ACTION_COLLECTION and
                                self.result == self.RESULT_COLLECTED and
                                self.from_deposit is not None and
                                self.from_deposit.client is not None and
                                not self.from_deposit.is_sinergia)
        deposit = (self.action == self.ACTION_DEPOSIT and
                   self.result == self.RESULT_IN_DEPOSIT and
                   self.to_deposit is not None)
        withdraw_from_central = (self.action == self.ACTION_COLLECTION and
                                 self.result == self.RESULT_COLLECTED and
                                 self.to_deposit is None and
                                 self.from_deposit is not None and
                                 self.from_deposit.client is None and
                                 self.from_deposit.is_central)
        withdraw_from_deposit = (self.action == self.ACTION_COLLECTION and
                                 self.result == self.RESULT_COLLECTED and
                                 self.to_deposit is None and
                                 self.from_deposit is not None and
                                 self.from_deposit.client is None and
                                 self.from_deposit.is_sinergia)
        withdraw_from_deposit = (self.action == self.ACTION_TRANSFER and
                                 self.result == self.RESULT_COLLECTED and
                                 self.to_deposit is None and
                                 (self.from_deposit is not None and
                                  self.from_deposit.client is None and
                                  self.from_deposit.is_sinergia))
        transfered = (self.action == self.ACTION_TRANSFER and
                      self.result == self.RESULT_TRANSFERED and
                      self.to_deposit is None and
                      self.from_deposit is None and
                      self.to_carrier is not None and
                      self.from_carrier is not None)
        delivered = (self.action == self.ACTION_DELIVERY_ATTEMPT and
                     self.result == self.RESULT_DELIVERED)
        rejected = (self.action == self.ACTION_DELIVERY_ATTEMPT and
                    self.result == self.RESULT_REJECTED_AT_DESTINATION)
        reprogramed = (self.action == self.ACTION_DELIVERY_ATTEMPT and
                       self.result == self.RESULT_REPROGRAMED)
        no_answer = (self.action == self.ACTION_DELIVERY_ATTEMPT and
                     self.result == self.RESULT_NO_ANSWER)
        other = (self.action == self.ACTION_DELIVERY_ATTEMPT and
                 self.result == self.RESULT_OTHER)

        if added:
            return ('Nuevo', 'agregado al sistema.')
        elif withdraw_from_origin:
            return ('En nuestras manos',
                    ("retirado del depósito de origen e ingresó"
                     " al circuito de distribución."))
        elif deposit:
            return ('En depósito',
                    ("ingresó en nuestro depósito '%s' y está"
                     " listo para su distribución." % self.to_deposit.name))
        elif withdraw_from_central:
            return ('Salida de depósito',
                    'en camino al domicilio del destinatario.')
        elif withdraw_from_deposit:
            return ('Salida de depósito',
                    'en camino al domicilio del desinatario.')
        elif transfered:
            return ('En camino',
                    ("retirado del circuito de distribución y"
                     " en camino al destinatario."))
        elif delivered:
            return ('Entregado', 'se entregó con éxito.')
        elif rejected:
            return ('Intento de entrega', 'el envío fue rechazado en destino.')
        elif reprogramed:
            return ('Intento de entrega', 'se reprogramó la entrega.')
        elif no_answer:
            return ('Intento de entrega',
                    ("no pudimos entregar el envío porque nadie "
                     "respondió en el domicilio de destino."))
        elif other:
            return ('Intento de entrega', 'otra causa.')
        return ('Error',
                'Ocurrió un error y no pudimos procesar la información.')

    def end_user_display(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Movimiento'
        verbose_name_plural = 'Movimientos'


@receiver(post_delete, sender=TrackingMovement)
def submission_delete(sender, instance, **kwargs):
    instance.proof.delete(False)
