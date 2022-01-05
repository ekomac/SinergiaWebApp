from django import forms
from .models import Attachment, Ticket


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
        """Before saving the ticket, save the files"""
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
