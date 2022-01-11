
from django import forms
from account.models import Account
from clients.models import Client
from summaries.models import Summary


class CustomaccountModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.full_name_formal + " (" + obj.username + ")"


class CreateSummaryForm(forms.ModelForm):

    client = forms.ModelChoiceField(
        queryset=Client.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}))

    employee = CustomaccountModelChoiceField(
        queryset=Account.objects.filter(client__isnull=True).exclude(
            role__in=['client']).order_by('last_name'),
        widget=forms.Select(attrs={'class': 'form-select'}),
        to_field_name='last_name')

    class Meta:
        model = Summary
        fields = ['date_from', 'date_to', 'client', 'employee', ]
        widgets = {
            'date_from': forms.TextInput(attrs={
                'class': 'form-control datepicker',
                'placeholder': 'Fecha desde', 'type': 'date'}),
            'date_to': forms.TextInput(attrs={
                'class': 'form-control datepicker',
                'placeholder': 'Fecha hasta', 'type': 'date'}),
            # 'client': forms.Select(attrs={'class': 'form-select'}),
            # 'employee': forms.Select(attrs={'class': 'form-select'}),
        }
