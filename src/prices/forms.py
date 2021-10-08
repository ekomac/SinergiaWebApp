from django import forms
from prices.models import DeliveryCode, FlexCode


class CreateDCodeForm(forms.ModelForm):

    code_attrs = {
        'class': 'form-control',
        'type': 'text',
        'pattern': '^[0-9]{1,3}$',
    }

    # if DeliveryCode.objects.all().count() > 0:
    #     last_code = DeliveryCode.objects.all().order_by('code')[:1].get()

    #     DeliveryCode.objects..first()
    #     code_attrs

    code = forms.CharField(label='Nombre del código', required=True,
                           widget=forms.TextInput(attrs=code_attrs),)

    price = forms.DecimalField(
        label='Precio base', required=True,
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
                               'pattern': '^F[0-9]{1,3}$',
                           }),)

    price = forms.DecimalField(
        label='Precio base', required=True,
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

    def clean_code(self, *args, **kwargs):
        code = self.cleaned_data.get("code")
        if FlexCode.objects.filter(code=code).exists():
            raise forms.ValidationError(f'El código "{code}" ya existe.')
        return code

    def clean_price(self, *args, **kwargs):
        price = self.cleaned_data.get("price")
        if FlexCode.objects.filter(price=price).exists():
            raise forms.ValidationError("Ya existe un código con ese precio.")
        return price


class UpdateDCodeForm(forms.ModelForm):
    pass


class UpdateFCodeForm(forms.ModelForm):

    code = forms.CharField(label='Nombre del código', required=True,
                           widget=forms.TextInput(attrs={
                               'class': 'form-control',
                               'type': 'text',
                               'pattern': '^F[0-9]{1,3}$',
                           }),)

    price = forms.DecimalField(
        label='Precio base', required=True,
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

    def clean_code(self, *args, **kwargs):
        code = self.cleaned_data.get("code")
        if FlexCode.objects.filter(code=code).exists():
            if id := self.instance.pk:
                if code != FlexCode.objects.get(id=id).code:
                    raise forms.ValidationError(
                        f'El código "{code}" ya existe.')
        return code

    def clean_price(self, *args, **kwargs):
        price = self.cleaned_data.get("price")
        if FlexCode.objects.filter(price=price).exists():
            if id := self.instance.pk:
                if price != FlexCode.objects.get(id=id).price:
                    raise forms.ValidationError(
                        "Ya existe un código con ese precio.")
        return price
