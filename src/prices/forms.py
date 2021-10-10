from django import forms
from django.forms.models import model_to_dict
from prices.models import DeliveryCode, FlexCode


class OnlyUpdatesError(Exception):
    pass


class CleanerMixin(forms.ModelForm):

    def clean_unique_or_error(self, key, error_msg):
        value = self.cleaned_data.get(key)
        print(value)
        if self.Meta.model.objects.filter(**{key: value}).exists():
            error = error_msg
            if '{' in error_msg or '}' in error_msg:
                error = error_msg.format(value)
            raise forms.ValidationError(error)
        return value

    def clean_unique_beyond_instance_or_error(self, key, error_msg):
        # Cause we are updating, we need id
        # If there isn't, this isn't an update
        if id := self.instance.pk:
            # Get value for given key
            value = self.cleaned_data.get(key)
            # If there isn't any database object with that value
            # for given property (given by the key)
            if self.Meta.model.objects.filter(**{key: value}).exists():
                # If value exists beyond the instance, it's because
                # it belongs to another instance.
                dict_model = model_to_dict(
                    self.Meta.model.objects.get(id=id))[key]
                if value != dict_model:
                    # So raise error
                    error = error_msg
                    if '{}' in error_msg:
                        error = error_msg.format(value)
                    raise forms.ValidationError(error)
            return value
        else:
            raise OnlyUpdatesError("This method only works for updating!")


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
