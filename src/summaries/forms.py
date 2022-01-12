
from datetime import datetime
from django import forms
from account.models import Account
from clients.models import Client
from summaries.models import Summary


class CustomaccountModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.full_name_formal + " (" + obj.username + ")"


class CreateSummaryForm(forms.ModelForm):

    what = forms.CharField(
        label='¿Qué?',
        widget=forms.TextInput())

    client = forms.ModelChoiceField(
        queryset=Client.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False)

    employee = CustomaccountModelChoiceField(
        queryset=Account.objects.filter(client__isnull=True).exclude(
            role__in=['client']).order_by('last_name'),
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False)

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
        }

    def clean(self):
        # Then call the clean() method of the super  class
        cleaned_data = super(CreateSummaryForm, self).clean()
        print("cleaned data", cleaned_data)
        date_from = cleaned_data['date_from']
        date_to = cleaned_data['date_to']
        if date_from > date_to:
            raise forms.ValidationError(
                "La fecha desde no puede ser mayor a la fecha hasta")
        if cleaned_data['what'] == 'client':
            cleaned_data['employee'] = None
        else:
            cleaned_data['client'] = None
        return cleaned_data
