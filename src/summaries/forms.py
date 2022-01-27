
from django import forms
from account.models import Account
from clients.models import Client
from summaries.models import ClientSummary, EmployeeSummary


class CustomAccountModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.full_name_formal + " (" + obj.username + ")"


class CreateEmployeeSummaryForm(forms.ModelForm):

    employee = CustomAccountModelChoiceField(
        queryset=Account.objects.filter(client__isnull=True).exclude(
            role__in=['client']).order_by('last_name'),
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False)

    class Meta:
        model = EmployeeSummary
        fields = ['date_from', 'date_to', 'employee', ]
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
        cleaned_data = super(CreateEmployeeSummaryForm, self).clean()
        date_from = cleaned_data['date_from']
        date_to = cleaned_data['date_to']
        if date_from > date_to:
            raise forms.ValidationError(
                "La fecha desde no puede ser mayor a la fecha hasta")
        return cleaned_data


class CreateClientSummaryForm(forms.ModelForm):

    client = forms.ModelChoiceField(
        queryset=Client.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False)

    class Meta:
        model = ClientSummary
        fields = ['date_from', 'date_to', 'client', ]
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
        cleaned_data = super(CreateClientSummaryForm, self).clean()
        date_from = cleaned_data['date_from']
        date_to = cleaned_data['date_to']
        if date_from > date_to:
            raise forms.ValidationError(
                "La fecha desde no puede ser mayor a la fecha hasta")
        return cleaned_data
