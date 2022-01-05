from django import forms
from .models import Client
from places.models import Town


class CreateClientForm(forms.ModelForm):

    deposit_address = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', }),
        required=True,
    )

    deposit_town = forms.ModelChoiceField(
        queryset=Town.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select', }),
        required=True,
    )

    deposit_zipcode = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', }),
        required=False,
    )

    deposit_phone = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', }),
        required=True,
    )

    deposit_email = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'type': 'email'}),
        required=True,
    )

    class Meta:
        model = Client
        fields = ['name', 'contact_name',
                  'contact_phone', 'contact_email', 'contract']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_email': forms.TextInput(attrs={'class': 'form-control',
                                                    'type': 'email'}),
            'contract': forms.FileInput(attrs={'class': 'form-control'}),
        }
