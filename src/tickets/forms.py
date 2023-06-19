from django import forms
from django.shortcuts import get_object_or_404
from .models import Attachment, Ticket, TicketMessage


class CreateTicketForm(forms.ModelForm):

    files = forms.FileField(
        required=False,
        widget=forms.FileInput(
            attrs={'multiple': True, 'class': 'form-control'}),
        label='Archivos adjuntos'
    )

    class Meta:
        model = Ticket
        fields = ['subject', 'msg', 'priority', ]
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'msg': forms.Textarea(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
        }

    def save(self, commit=True):
        """After saving the ticket, save the files"""
        # get current ticket instance
        ticket = self.instance
        if commit:
            # save the ticket
            ticket.save()
            # For each file, create a File obj and save it
            for file in self.files.getlist('files'):
                Attachment(file=file, ticket=ticket).save()
        # Return the ticket instance (just saved or previously saved)
        return ticket


class AddAttachmentsToTicketForm(forms.Form):

    file2s = forms.FileField(
        required=False,
        widget=forms.FileInput(
            attrs={'multiple': True, 'class': 'form-control'}),
        label='Archivos adjuntos'
    )

    def save(self, ticket_id, commit=True) -> list[Attachment]:
        """Save the files"""
        # get current ticket instance
        ticket = get_object_or_404(Ticket, pk=ticket_id)
        attachments = []
        if commit:
            # For each file, create a File obj and save it
            for file in self.files.getlist('files'):
                attachment = Attachment(file=file, ticket=ticket)
                attachment.save()
                attachments.append(attachment)

        return attachments


class CreateMessageForm(forms.ModelForm):

    class Meta:
        model = TicketMessage
        fields = ['created_by', 'msg', 'ticket']
        widgets = {
            'msg': forms.TextInput(attrs={
                'id': 'post-msg',
                'required': True,
                'placeholder': 'Escribí tu mensaje...'
            }),
        }
