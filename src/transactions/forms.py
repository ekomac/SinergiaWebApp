from decimal import Decimal
from django import forms
from transactions.models import Transaction


class TransactionForm(forms.ModelForm):

    class Meta:
        model = Transaction
        fields = [
            'date', 'category', 'amount',
            'description', 'summary',
            'transaction_number', 'proof_of_payment',
        ]
        widgets = {
            'date': forms.DateInput(
                attrs={'type': 'date'}),
            'category': forms.Select(
                attrs={'class': 'form-select', 'required': True}),
            'amount': forms.NumberInput(
                attrs={'step': '0.01'}),
            'description': forms.Textarea(
                attrs={'rows': '3'}),
            'summary': forms.Select(
                attrs={'class': 'form-select'}),
            'transaction_number': forms.TextInput(
                attrs={'class': 'form-control'}),
            'proof_of_payment': forms.FileInput(
                attrs={'class': 'form-control'}),
        }

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if Decimal(str(amount)) == Decimal(0):
            raise forms.ValidationError('El importe no puede ser 0.')
        return amount
