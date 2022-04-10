from django.conf import settings
from django.core.mail import send_mail
from django.db import models
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.urls import reverse

from account.models import Account


def upload_location(instance, filename):
    date = instance.date_created.strftime('%Y-%m-%d_%H-%M-%S')
    file_path = 'ticket_images/{ticket_id}/{date}-{filename}'.format(
        ticket_id=str(instance.ticket.id), date=date, filename=filename)
    return file_path


class Attachment(models.Model):
    """
    Model to store the images/files of a ticket.
    """
    date_created = models.DateTimeField(auto_now_add=True)
    file = models.FileField(
        upload_to=upload_location,
        blank=False,
        null=False,
        verbose_name="Attachment"
    )

    ticket = models.ForeignKey(
        'tickets.Ticket',
        blank=False,
        null=False,
        verbose_name="Ticket",
        on_delete=models.CASCADE
    )

    def __str__(self):
        return 'Archivo: {path} de {ticket}'.format(
            path=self.file.path,
            ticket=self.ticket
        )


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

    def __str__(self):
        return 'Ticket #{pk}: {subject} con prioridad {prioridad}'.format(
            pk=self.pk,
            subject=self.subject,
            prioridad=self.get_priority_display()
        )


@receiver(pre_delete, sender=Ticket)
def ticket_delete(sender, instance, **kwargs):
    """
    Delete the files associated with a ticket when the ticket is deleted.
    """
    for file in instance.attachment_set.all():
        file.delete(False)


HTML_BODY = """<h1>Se ha creado un <a href='{url}'>nuevo ticket</a> en el sistema.</h1>
<h3>Ticket #{pk}: {subject} con prioridad {prioridad}</h3>
<p><b>Mensaje</b>: {msg}</p>
<p><b>Autor</b>: <a href='{user_url}'>{author} ({author_name})</a></p>
"""


@receiver(post_save, sender=Ticket)
def notify_superusers(sender, instance, created, **kwargs):
    if created:
        subject = 'Nuevo ticket en el sistema'
        msg = """Se ha creado un nuevo ticket en el sistema.\n\n
Ticket #{pk}: {subject} con prioridad {prioridad}\n
Mensaje: {msg}\n\n
Autor: {created_by}\n\n""".format(
            pk=instance.pk,
            subject=instance.subject,
            prioridad=instance.get_priority_display(),
            msg=instance.msg,
            created_by=instance.created_by.full_name
        )
        url = reverse('tickets:detail', kwargs={'pk': instance.pk})
        base_url = 'https://www.sinergiasoftware.xyz'
        url = base_url + url
        user_url = reverse('account:employees-detail', kwargs={
                           'pk': instance.created_by.pk})
        user_url = base_url + user_url
        html_msg = HTML_BODY.format(
            url=url,
            pk=instance.pk,
            subject=instance.subject,
            prioridad=instance.get_priority_display(),
            msg=instance.msg,
            user_url=user_url,
            author=instance.created_by.username,
            author_name=instance.created_by.full_name
        )
        recipient_list = Account.objects.filter(
            is_superuser=True).values_list('email', flat=True)
        send_mail(
            subject=subject,
            message=msg,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            html_message=html_msg
        )
