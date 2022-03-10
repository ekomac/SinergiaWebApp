from django import forms
from account.models import Account
from prices.models import DeliveryCode, FlexCode
from utils.forms import CleanerMixin
from places.models import Partido, Town, Zone


class UpdatePartidoForm(forms.ModelForm):

    zone = forms.ModelChoiceField(
        label="Zona", required=False,
        queryset=Zone.objects.all(),
        widget=forms.Select(attrs={
            'class': ' form-select',
        }),
    )

    class Meta:
        model = Partido
        fields = ['zone']


class BulkEditPartidoForm(forms.Form):

    zone = forms.ModelChoiceField(
        label="Zona", required=False,
        queryset=Zone.objects.all(),
        widget=forms.Select(attrs={
            'class': ' form-select',
        }),
    )


class UpdateTownForm(CleanerMixin, forms.ModelForm):

    delivery_code = forms.ModelChoiceField(
        label="Código de mensajería", required=False,
        queryset=DeliveryCode.objects.all(),
        widget=forms.Select(attrs={
            'class': ' form-select',
        }),
    )

    flex_code = forms.ModelChoiceField(
        label="Código de flex", required=False,
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


class BulkEditTownDeliveryForm(forms.Form):

    delivery_code = forms.ModelChoiceField(
        label="Código de mensajería", required=False,
        queryset=DeliveryCode.objects.all(),
        widget=forms.Select(attrs={
            'class': ' form-select',
        }),
    )


class BulkEditTownFlexForm(forms.Form):

    flex_code = forms.ModelChoiceField(
        label="Código de flex", required=False,
        queryset=FlexCode.objects.all(),
        widget=forms.Select(attrs={
            'class': ' form-select',
        }),
    )


class BaseZoneForm(CleanerMixin, forms.ModelForm):
    selected_partidos_ids = forms.CharField(required=False)

    name = forms.CharField(
        label="Nombre", required=True,
        widget=forms.TextInput(attrs={
            'class': ' form-control',
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


class AddZoneForm(BaseZoneForm):

    def clean_name(self, *args, **kwargs):
        return self.clean_unique_or_error(
            'name', 'Ya existe una zona con ese nombre')


class AddZoneForm2(BaseZoneForm):

    partidos = forms.ModelMultipleChoiceField(
        label="Partidos", required=False,
        queryset=Partido.objects.all(),
        widget=forms.SelectMultiple(attrs={
            'class': ' form-select',
            'size': 10,
        }),
    )

    towns = forms.ModelMultipleChoiceField(
        label="Localidades", required=False,
        queryset=Town.objects.all(),
        widget=forms.SelectMultiple(attrs={
            'class': ' form-select',
            'size': 10,
        }),
    )

    def clean_name(self, *args, **kwargs):
        return self.clean_unique_or_error(
            'name', 'Ya existe una zona con ese nombre')

    def save(self, commit=True):
        zone = super().save(commit)
        if self.cleaned_data['partidos']:
            zone.partidos.add(*self.cleaned_data['partidos'])
        print(self.cleaned_data['partidos'])
        # zone.partidos.add(*self.cleaned_data['partidos'])
        return zone


class UpdateZoneForm(BaseZoneForm):

    def clean_name(self, *args, **kwargs):
        return self.clean_unique_beyond_instance_or_error(
            'name', 'Ya existe una zona con ese nombre')
