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
        max_length=1, choices=CLOSED_REASONS,
        blank=True, null=True, verbose_name="Razón de cierre")
    closed_msg = models.TextField(
        blank=True, null=True, verbose_name="Mensaje de cierre")

    def __str__(self):
        return 'Ticket #{pk}: {subject} con prioridad {prioridad}'.format(
            pk=self.pk,
            subject=self.subject,
            prioridad=self.get_priority_display()
        )


class TicketMessage(models.Model):

    date_created = models.DateTimeField(
        auto_now_add=True, verbose_name="Creación")
    created_by = models.ForeignKey(
        'account.Account',
        on_delete=models.SET_NULL,
        verbose_name="Autor",
        blank=True, null=True, default=None)
    msg = models.TextField(blank=False, null=False, verbose_name="Mensaje")
    ticket = models.ForeignKey(
        'tickets.Ticket',
        blank=False,
        null=False,
        verbose_name="Ticket",
        on_delete=models.CASCADE
    )

    def __str__(self):
        return 'Mensaje de {user} en {ticket}'.format(
            user=self.created_by.username,
            ticket=self.ticket.subject
        )

    class Meta:
        ordering = ['date_created']
        verbose_name = "Mensaje"
        verbose_name_plural = "Mensajes"


@receiver(pre_delete, sender=Ticket)
def ticket_delete(sender, instance, **kwargs):
    """
    Delete the files associated with a ticket when the ticket is deleted.
    """
    for file in instance.attachment_set.all():
        file.delete(False)


NEW_TICKET_HTML_BODY = """<h1>Se ha creado un <a href='{url}'>nuevo ticket</a> en el sistema.</h1>
<h3>Ticket #{pk}: {subject} con prioridad {prioridad}</h3>
<p><b>Mensaje</b>: {msg}</p>
<p><b>Autor</b>: <a href='{user_url}'>{author} ({author_name})</a></p>
"""


@receiver(post_save, sender=Ticket)
def notify_new_ticket_to_superusers(sender, instance, created, **kwargs):
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
        html_msg = NEW_TICKET_HTML_BODY.format(
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


@receiver(post_save, sender=Ticket)
def add_message_to_chat(sender, instance, created, **kwargs):
    if created:
        ticket_message = TicketMessage(
            created_by=instance.created_by,
            msg=instance.msg,
            ticket=instance
        )
        ticket_message.save()


NEW_MESSAGE_IN_TICKET = (
    'Se ha registrado un nuevo mensaje en el ticket "{ticket}".\n\n'
    '{user} escribió:\n'
    '"{msg}"\n\n'
    '{date}\n\n'
)

NEW_MESSAGE_IN_TICKET_HTML_BODY = (
    '<h1>Se ha registrado un nuevo mensaje en el ticket '
    '<a href="{ticket_url}">{ticket_subject}</a>.</h1>'
    '<div style="border: 1px solid grey; padding: 1rem; margin: auto;">'
    '<p><a href="{author_url}">@{author_username}</a> escribió:</p>'
    '<p>"{msg}"</p>'
    '<p>El {date} a las {time}</p>'
    '</div>'
)


@receiver(post_save, sender=TicketMessage)
def notify_new_message_in_ticket(sender, instance, created, **kwargs):
    if created:
        subject = "Nuevo mensaje de ticket"
        msg = NEW_MESSAGE_IN_TICKET.format(
            ticket=instance.ticket.subject,
            user=instance.created_by,
            msg=instance.msg,
            date=instance.date_created
        )
        url = reverse('tickets:detail', kwargs={'pk': instance.ticket.pk})
        base_url = 'https://www.sinergiasoftware.xyz'
        url = base_url + url
        user_url = reverse('account:employees-detail', kwargs={
                           'pk': instance.created_by.pk})
        user_url = base_url + user_url
        html_msg = NEW_MESSAGE_IN_TICKET_HTML_BODY.format(
            ticket_url=base_url,
            ticket_subject=instance.ticket.subject,
            author_url=user_url,
            author_username=instance.created_by.username,
            msg=instance.msg,
            date=instance.date_created.strftime('%d/%m/%Y'),
            time=instance.date_created.strftime('%H:%M:%S'),
        )
        print("Quien creo el mensaje", instance.created_by)
        print("Quien creo el ticket", instance.ticket.created_by)
        if instance.created_by.pk == instance.ticket.created_by.pk:
            recipient_list = Account.objects.filter(
                is_superuser=True).values_list('email', flat=True)
        else:
            recipient_list = [instance.ticket.created_by.email]
        print("recipient_list", recipient_list)
        result = send_mail(
            subject=subject,
            message=msg,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            html_message=html_msg
        )
        print(result)
