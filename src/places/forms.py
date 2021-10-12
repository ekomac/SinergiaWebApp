from django import forms
from prices.models import DeliveryCode, FlexCode
from utils.forms import CleanerMixin
from places.models import Town


class UpdateTownForm(CleanerMixin, forms.ModelForm):

    delivery_code = forms.ModelChoiceField(
        label="Código de mensajería", required=True,
        queryset=DeliveryCode.objects.all(),
        widget=forms.Select(attrs={
            'class': ' form-select',
        }),
    )

    flex_code = forms.ModelChoiceField(
        label="Código de flex", required=True,
        queryset=FlexCode.objects.all(),
        widget=forms.Select(attrs={
            'class': ' form-select',
        }),
    )

    class Meta:
        model = Town
        fields = [
            'delivery_code',
            'flex_code',
        ]
