from django.conf import settings
from django.core.mail import send_mail
from django.db import models
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.urls import reverse

from account.models import Account
from .mailing import messages


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
        blank=True, null=True, default=None,
        related_name="tickets_created")
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
    closed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Cerrado por",
        blank=True, null=True, default=None,
        related_name="tickets_closed")

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


@receiver(post_save, sender=Ticket)
def send_notifications_for_ticket(sender, instance, created, **kwargs):
    if created:
        send_mail_to_superusers_new_ticket_created(instance)
        add_first_message_to_chat(instance)
    else:
        # Was closed by superuser
        if instance.status == '3':
            if instance.closed_by.is_superuser:
                send_mail_to_users_ticket_closed(instance)
            else:
                send_mail_to_superusers_ticket_closed(instance)


def add_first_message_to_chat(ticket: Ticket):
    ticket_message = TicketMessage(
        created_by=ticket.created_by,
        msg=ticket.msg,
        ticket=ticket
    )
    ticket_message.save()


@receiver(post_save, sender=TicketMessage)
def notify_new_message_in_ticket(sender, instance, created, **kwargs):
    if created:
        send_mail_new_message_to_counterpart(instance)


def send_mail_to_superusers_new_ticket_created(ticket: Ticket):
    subject = 'Nuevo ticket en el sistema'
    msg = messages['PLAIN_TICKET_CREATED'].format(
        pk=ticket.pk,
        subject=ticket.subject,
        prioridad=ticket.get_priority_display(),
        msg=ticket.msg,
        created_by=ticket.created_by.full_name
    )
    url = reverse('tickets:detail', kwargs={'pk': ticket.pk})
    base_url = 'https://www.sinergiasoftware.xyz'
    url = base_url + url
    user_url = reverse('account:employees-detail', kwargs={
        'pk': ticket.created_by.pk})
    user_url = base_url + user_url
    html_msg = messages['HTML_TICKET_CREATED'].format(
        url=url,
        pk=ticket.pk,
        subject=ticket.subject,
        prioridad=ticket.get_priority_display(),
        msg=ticket.msg,
        user_url=user_url,
        author=ticket.created_by.username,
        author_name=ticket.created_by.full_name
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


def send_mail_to_superusers_ticket_closed(ticket: Ticket):
    if ticket.closed_reason in ['1', '4']:
        action = ticket.closed_reason == '1' and \
            'canceló' or 'marcó como resuelto'
        subject = f'Se {action} un ticket'
        msg = messages['PLAIN_TICKET_CLOSED_FOR_SUPERUSER'].format(
            action=action,
            pk=ticket.pk,
            subject=ticket.subject,
            prioridad=ticket.get_priority_display(),
            closed_reason=ticket.get_closed_reason_display(),
            closed_message=ticket.closed_msg,
            created_by=ticket.created_by.full_name
        )
        url = reverse('tickets:detail', kwargs={'pk': ticket.pk})
        base_url = 'https://www.sinergiasoftware.xyz'
        url = base_url + url
        user_url = reverse('account:employees-detail', kwargs={
                           'pk': ticket.created_by.pk})
        user_url = base_url + user_url
        html_msg = messages['HTML_TICKET_CLOSED_FOR_SUPERUSER'].format(
            author1=ticket.created_by.full_name,
            action=action,
            url=url,
            pk=ticket.pk,
            subject=ticket.subject,
            prioridad=ticket.get_priority_display(),
            closed_reason=ticket.get_closed_reason_display(),
            closed_message=ticket.closed_msg,
            user_url=user_url,
            author2=ticket.created_by.username,
            author_name=ticket.created_by.full_name
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


def send_mail_to_users_ticket_closed(ticket: Ticket):
    subject = 'Se cerró un ticket'
    msg = messages['PLAIN_TICKET_CLOSED_FOR_USER'].format(
        pk=ticket.pk,
        subject=ticket.subject,
        prioridad=ticket.get_priority_display(),
        closed_reason=ticket.get_closed_reason_display(),
        closed_message=ticket.closed_msg,
        created_by=ticket.created_by.full_name
    )
    url = reverse('tickets:detail', kwargs={'pk': ticket.pk})
    base_url = 'https://www.sinergiasoftware.xyz'
    url = base_url + url
    user_url = reverse('account:employees-detail', kwargs={
        'pk': ticket.created_by.pk})
    user_url = base_url + user_url
    html_msg = messages['HTML_TICKET_CLOSED_FOR_USER'].format(
        url=url,
        pk=ticket.pk,
        subject=ticket.subject,
        prioridad=ticket.get_priority_display(),
        closed_reason=ticket.get_closed_reason_display(),
        closed_message=ticket.closed_msg,
        user_url=user_url,
        author=ticket.created_by.username,
        author_name=ticket.created_by.full_name
    )
    recipient_list = [ticket.created_by.email]
    send_mail(
        subject=subject,
        message=msg,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list,
        html_message=html_msg
    )


def send_mail_new_message_to_counterpart(message: TicketMessage):
    subject = "Nuevo mensaje de ticket"
    msg = messages['PLAIN_NEW_MESSAGE_IN_TICKET'].format(
        ticket=message.ticket.subject,
        user=message.created_by,
        msg=message.msg,
        date=message.date_created
    )
    url = reverse('tickets:detail', kwargs={'pk': message.ticket.pk})
    base_url = 'https://www.sinergiasoftware.xyz'
    url = base_url + url
    user_url = reverse('account:employees-detail', kwargs={
                       'pk': message.created_by.pk})
    user_url = base_url + user_url
    html_msg = messages['HTML_NEW_MESSAGE_IN_TICKET'].format(
        ticket_url=base_url,
        ticket_subject=message.ticket.subject,
        author_url=user_url,
        author_username=message.created_by.username,
        msg=message.msg,
        date=message.date_created.strftime('%d/%m/%Y'),
        time=message.date_created.strftime('%H:%M:%S'),
    )
    if message.created_by.pk == message.ticket.created_by.pk:
        recipient_list = Account.objects.filter(
            is_superuser=True).values_list('email', flat=True)
    else:
        recipient_list = [message.ticket.created_by.email]
    send_mail(
        subject=subject,
        message=msg,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list,
        html_message=html_msg
    )
