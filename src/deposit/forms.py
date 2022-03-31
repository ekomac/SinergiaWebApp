from django import forms
from deposit.models import Deposit


class CreateDepositForm(forms.ModelForm):

    class Meta:
        model = Deposit
        fields = ['client', 'name', 'address', 'zip_code',
                  'town', 'phone', 'email', 'is_sinergia',
                  'is_central', 'is_active']
        widgets = {
            'client': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'zip_code': forms.TextInput(attrs={'class': 'form-control'}),
            'town': forms.Select(attrs={'class': 'form-select'}),
            'phone': forms.TextInput(
                attrs={'class': 'form-control', 'type': 'tel'}),
            'email': forms.TextInput(
                attrs={'class': 'form-control', 'type': 'email'}),
            'is_sinergia': forms.CheckboxInput(
                attrs={'class': 'form-control'}),
            'is_central': forms.CheckboxInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-control'}),
        }
