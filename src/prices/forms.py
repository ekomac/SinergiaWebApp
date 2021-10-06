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

    class Meta:
        model = FlexCode
        fields = [
            'code',
            'price',
        ]
