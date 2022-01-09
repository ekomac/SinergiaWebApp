
from django import forms
from summaries.models import Summary


class CreateSummaryForm(forms.ModelForm):

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
            'client': forms.Select(attrs={'class': 'form-select'}),
            'employee': forms.Select(attrs={'class': 'form-select'}),
        }
