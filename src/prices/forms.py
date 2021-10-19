from django import forms
from utils.forms import CleanerMixin
from prices.models import DeliveryCode, FlexCode


class BaseDeliveryCodeForm(CleanerMixin):

    code = forms.CharField(label='Nombre del código', required=True,
                           widget=forms.TextInput(attrs={
                               'class': 'form-control',
                               'type': 'text',
                               'pattern': '^D[0-9]{1,3}$',
                           }),)

    price = forms.DecimalField(label='Precio base', required=True,
                               widget=forms.TextInput(
                                   attrs={
                                       'class': 'form-control',
                                       'type': 'number',
                                       'placeholder': '0',
                                       'min': '0',
                                       'max': '999999.99',
                                       'step': '1'
                                   }),)

    class Meta:
        model = DeliveryCode
        fields = [
            'code',
            'price',
        ]


class CreateDeliveryCodeForm(BaseDeliveryCodeForm, forms.ModelForm):

    def clean_code(self, *args, **kwargs):
        return self.clean_unique_or_error(
            'code', 'El código "{}" ya existe.')

    def clean_price(self, *args, **kwargs):
        return self.clean_unique_or_error(
            'price', "Ya existe un código con ese precio")


class UpdateDeliveryCodeForm(BaseDeliveryCodeForm, forms.ModelForm):

    def clean_code(self, *args, **kwargs):
        return self.clean_unique_beyond_instance_or_error(
            'code', 'El código "{}" ya existe.')

    def clean_price(self, *args, **kwargs):
        return self.clean_unique_beyond_instance_or_error(
            'price', "Ya existe un código con ese precio")


class BaseFlexCodeForm(CleanerMixin):

    code = forms.CharField(label='Nombre del código', required=True,
                           widget=forms.TextInput(attrs={
                               'class': 'form-control',
                               'type': 'text',
                               'pattern': '^F[0-9]{1,3}$',
                           }),)

    price = forms.DecimalField(label='Precio base', required=True,
                               widget=forms.TextInput(
                                   attrs={
                                       'class': 'form-control',
                                       'type': 'number',
                                       'placeholder': '0',
                                       'min': '0',
                                       'max': '999999.99',
                                       'step': '1'
                                   }),)

    already_exists_code = 'El código flex "{}" ya existe.'
    already_exists_price = "Ya existe un código flex con ese precio"

    class Meta:
        model = FlexCode
        fields = [
            'code',
            'price',
        ]


class CreateFlexCodeForm(BaseFlexCodeForm, forms.ModelForm):

    def clean_code(self, *args, **kwargs):
        return self.clean_unique_or_error(
            'code', self.already_exists_code)

    def clean_price(self, *args, **kwargs):
        return self.clean_unique_or_error(
            'price', self.already_exists_price)


class UpdateFlexCodeForm(BaseFlexCodeForm, forms.ModelForm):

    def clean_code(self, *args, **kwargs):
        return self.clean_unique_beyond_instance_or_error(
            'code', self.already_exists_code)

    def clean_price(self, *args, **kwargs):
        return self.clean_unique_beyond_instance_or_error(
            'price', self.already_exists_price)


class BaseBulkEditPercentageForm(forms.Form):
    percentage = forms.CharField(
        label="Nombre", required=True,
        widget=forms.TextInput(attrs={
            'class': ' form-control',
            'type': 'number'
        }),
    )


class BulkEditFlexCodePercentageForm(BaseBulkEditPercentageForm):
