from django import forms
from .models import Client, Discount
from deposit.models import Deposit
from places.models import Town


class CreateClientForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(CreateClientForm, self).__init__(*args, **kwargs)

    deposit_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', }),
        required=True,
    )

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
        required=False,
    )

    deposit_email = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'type': 'email'}),
        required=False,
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

    def save(self, commit=True):
        """After saving the client, save the deposit"""
        # get current ticket instance
        client = self.instance
        if commit:
            # save the ticket
            if self.user is not None:
                client.crcreated_by = self.user
                client.save()

                print("aca estamos")

                Deposit(
                    client=client,
                    name=self.cleaned_data['deposit_name'],
                    address=self.cleaned_data['deposit_address'],
                    zip_code=self.cleaned_data['deposit_zipcode'],
                    town=self.cleaned_data['deposit_town'],
                    phone=self.cleaned_data['deposit_phone'],
                    email=self.cleaned_data['deposit_email'],
                    created_by=self.user,
                ).save()
        # Return the client instance (just saved or previously saved)
        return client


class EditClientForm(forms.ModelForm):

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

    def save(self, commit=True):
        client = self.instance
        client.name = self.cleaned_data['name']
        client.contact_name = self.cleaned_data['contact_name']
        client.contact_phone = self.cleaned_data['contact_phone']
        client.contact_email = self.cleaned_data['contact_email']

        if self.cleaned_data['contract']:
            client.contract = self.cleaned_data['contract']

        if commit:
            client.save()
        return client


class CreateDiscountForm(forms.ModelForm):

    class Meta:
        model = Discount
        fields = ['amount', 'partidos', 'is_for_flex']
