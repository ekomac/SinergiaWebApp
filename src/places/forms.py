from django import forms
from account.models import Account
from prices.models import DeliveryCode, FlexCode
from utils.forms import CleanerMixin
from places.models import Partido, Town, Zone


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


class AddZoneForm(CleanerMixin, forms.ModelForm):

    selected_partidos_ids = forms.CharField(required=False)

    name = forms.CharField(
        label="Nombre", required=True,
        widget=forms.TextInput(attrs={
            'class': ' form-select',
        }),
    )

    asigned_to = forms.ModelChoiceField(
        label="Asignada a", required=False,
        queryset=Account.objects.all(),
        widget=forms.Select(attrs={
            'class': ' form-select',
        }),
    )

    class Meta:
        model = Zone
        fields = [
            'name',
            'asigned_to',
        ]

    def clean_name(self, *args, **kwargs):
        return self.clean_unique_or_error(
            'name', 'Ya existe una zona con ese nombre')


class UpdateZoneForm(CleanerMixin, forms.ModelForm):

    name = forms.CharField(
        label="Nombre", required=True,
        widget=forms.TextInput(attrs={
            'class': ' form-select',
        }),
    )

    asigned_to = forms.ModelChoiceField(
        label="Asignada a", required=False,
        queryset=Account.objects.all(),
        widget=forms.Select(attrs={
            'class': ' form-select',
        }),
    )

    class Meta:
        model = Zone
        fields = [
            'name',
            'asigned_to',
        ]

    def clean_name(self, *args, **kwargs):
        return self.clean_unique_beyond_instance_or_error(
            'name', 'Ya existe una zona con ese nombre')


class UpdatePartidosZone(forms.ModelForm):

    class Meta:
        model = Partido
        fields = ['is_amba', 'amba_zone']
        exclude = ('name', 'province')
