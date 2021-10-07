from django import forms
from prices.models import DeliveryCode, FlexCode


class CreateDCodeForm(forms.ModelForm):

    class Meta:
        model = DeliveryCode
        fields = [
            'code',
            'price',
        ]


class CreateFCodeForm(forms.ModelForm):

    code = forms.CharField(label='Nombre del código', required=True,
                           widget=forms.TextInput(attrs={
                                 'class': 'form-control',
                                 'type': 'text',
                           }),)

    price = forms.DecimalField(
        label='Precio base', required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'type': 'number',
                'placeholder': '0',
                'min': '0',
                'max': '999999999',
                'step': '1'
            })
    )

    class Meta:
        model = FlexCode
        fields = [
            'code',
            'price',
        ]
