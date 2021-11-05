from django import forms
from clients.models import Client


class WithdrawForm(forms.Form):
    """
    Form to withdraw envios
    """
    client = forms.ModelChoiceField(
        queryset=Client.objects.all(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def clean(self):
        cleaned_data = super().clean()
        client = cleaned_data.get('client')
        print(client)
        return cleaned_data

    def save(self):
        cleaned_data = self.cleaned_data
        print(cleaned_data)
