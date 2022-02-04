import hashlib
from django import forms
from django.core.validators import FileExtensionValidator
from deposit.models import Deposit
from envios.bulkutil.exceptions import (
    InvalidExcelFileError, InvalidPdfFileError)
from envios.bulkutil.extractor import Extractor
from envios.models import BulkLoadEnvios, Envio
from clients.models import Client
from places.models import Town


class BulkLoadEnviosForm(forms.ModelForm):

    client = forms.ModelChoiceField(
        label="Cliente", required=True,
        queryset=Client.objects.all(),
        widget=forms.Select(attrs={
            'class': ' form-select',
        }),
    )

    deposit = forms.ModelChoiceField(
        label="Deposit", required=True,
        queryset=Deposit.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': 'required',
        }),
    )

    file = forms.FileField(
        allow_empty_file=False,
        label="Archivo con envíos(PDF MercadoLibre o TiendaNube, Excel)",
        required=True,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
        }),
        validators=[FileExtensionValidator(['pdf', 'xlsx'])])

    def __init__(self, user=None, *args, **kwargs):
        super(BulkLoadEnviosForm, self).__init__(*args, **kwargs)
        self.author = user
        self.file_content = None
        self.result = None
        self.found_errors = None
        self.requires_manual_fix = False
        self.cells_to_paint = None

    class Meta:
        model = BulkLoadEnvios
        fields = ['client']

    def clean_file(self):
        file = self.cleaned_data.get('file')
        self.hash_from_file = hashlib.md5(file.read()).hexdigest()
        file.file.seek(0)
        if BulkLoadEnvios.objects.filter(
                hashed_file=self.hash_from_file,
                load_status=BulkLoadEnvios.LOADING_STATUS_FINISHED).exists():
            raise forms.ValidationError(
                "Ya se cargó un archivo con los mismos datos")
        try:
            extractor = Extractor()
            result = extractor.get_shipments(file)
            self.result = result['result']
            self.found_errors = result['errors']
            self.requires_manual_fix = result['needs_manual_fix']
            self.cells_to_paint = result['cells_to_paint']
            return file
        except InvalidPdfFileError:
            raise forms.ValidationError("El PDF proporcionado no es\
                ni de MercadoLibre ni de TiendaNube")
        except InvalidExcelFileError:
            raise forms.ValidationError("El archivo de Excel proporcionada \
                no es válido.")

    def save(self, commit=True):
        bulk_load = self.instance
        # If a bulk_load with same hash and not finished
        # is found, delete it before saving this
        if BulkLoadEnvios.objects.filter(
                hashed_file=self.hash_from_file,
                load_status=BulkLoadEnvios.LOADING_STATUS_PROCESSING).exists():
            BulkLoadEnvios.objects.filter(
                hashed_file=self.hash_from_file,
                load_status=BulkLoadEnvios.LOADING_STATUS_PROCESSING).delete()
        bulk_load.hashed_file = self.hash_from_file
        bulk_load.created_by = self.author
        if not self.found_errors:
            bulk_load.load_status = BulkLoadEnvios.LOADING_STATUS_FINISHED
        bulk_load.client = self.cleaned_data['client']
        bulk_load.deposit = self.cleaned_data['deposit']
        bulk_load.csv_result = self.result
        bulk_load.errors = self.found_errors
        bulk_load.requires_manual_fix = self.requires_manual_fix
        bulk_load.cells_to_paint = self.cells_to_paint
        if commit:
            bulk_load.save()
        return bulk_load


class CreateEnvioForm(forms.ModelForm):

    def __init__(self, client: Client = None, *args, **kwargs):
        super(CreateEnvioForm, self).__init__(*args, **kwargs)
        self.client = client

    client = forms.ModelChoiceField(
        label="Cliente", required=True,
        queryset=Client.objects.all(),
        widget=forms.Select(attrs={
            'class': ' form-select',
        }),
    )

    detail = forms.CharField(label='Detalle', required=True,
                             initial="0-1",
                             widget=forms.TextInput(attrs={
                                 'class': 'form-control',
                                 'type': 'text',
                             }),)

    name = forms.CharField(
        label='Nombre del destinatario', required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'type': 'text',
                'placeholder': 'Juan Pérez',
            }),
    )

    doc = forms.CharField(
        label='DNI', required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'type': 'text',
                'placeholder': '30.123.567',
                'pattern': r'^\d{7,8}$',
            }),
    )

    phone = forms.CharField(
        label='Teléfono', required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'type': 'text',
                'placeholder': '11 1234-5678',
                'pattern': r'^\d{4,15}$'
            })
    )

    street = forms.CharField(
        label='Domicilio', required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'type': 'text',
                'placeholder': 'Av. del Libertador 256',
            })
    )

    remarks = forms.CharField(
        label='Domicilio', required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'type': 'text',
                'placeholder': 'Portones negros',
            })
    )

    town = forms.ModelChoiceField(
        label="Localidad", required=True,
        queryset=Town.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': 'required',
        }),
    )

    zipcode = forms.CharField(
        label='Código postal', required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'type': 'text',
                'placeholder': '1663',
                'pattern': r'^\d*$',
            })
    )

    max_delivery_date = forms.DateField(
        label='Fecha máxima de entrega', required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control datepicker',
                'placeholder': 'Fecha desde',
                'type': 'date',
            })
    )

    is_flex = forms.BooleanField(
        label='¿Es envío de Flex?', required=False,
        initial=False,
        widget=forms.CheckboxInput(
            attrs={
                'class': 'form-check-input',
                'type': 'checkbox',
            })
    )

    flex_id = forms.CharField(
        label='Tracking ID de Flex', required=False,
        widget=forms.TextInput(
            attrs={
                'type': 'text',
                'class': 'form-control',
                'placeholder': 'N° de ID',
                'disabled': 'disabled'
            }
        )
    )

    recipient_charge = forms.DecimalField(
        label='Cobrar al cliente', required=False,
    )

    deposit = forms.ModelChoiceField(
        label="Deposit", required=True,
        queryset=Deposit.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': 'required',
        }),
    )

    def validate_flex_id(self):
        if self.cleaned_data['is_flex']:
            if not self.cleaned_data['flex_id']:
                raise forms.ValidationError(
                    'El campo Tracking ID de Flex es obligatorio')

    class Meta:
        model = Envio
        fields = [
            'client',
            'detail',
            'name',
            'doc',
            'phone',
            'street',
            'remarks',
            'town',
            'zipcode',
            'charge',
            'max_delivery_date',
            'is_flex',
            'flex_id',
            'delivery_schedule',
            'deposit',
        ]
        widgets = {
            'delivery_schedule': forms.Select(attrs={
                'class': 'form-select',
            })
        }


class UpdateEnvioForm(forms.ModelForm):

    client = forms.ModelChoiceField(
        label="Cliente", required=True,
        queryset=Client.objects.all(),
        widget=forms.Select(attrs={
            'class': ' form-select',
        }),
    )

    detail = forms.CharField(label='Detalle', required=True,
                             initial="0-1",
                             widget=forms.TextInput(attrs={
                                 'class': 'form-control',
                                 'type': 'text',
                             }),)

    name = forms.CharField(
        label='Nombre del destinatario', required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'type': 'text',
                'placeholder': 'Juan Pérez',
            }),
    )

    doc = forms.CharField(
        label='DNI', required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'type': 'text',
                'placeholder': '30.123.567',
                'pattern': r'^\d{7,8}$',
            }),
    )

    phone = forms.CharField(
        label='Teléfono', required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'type': 'text',
                'placeholder': '11 1234-5678',
                'pattern': r'^\d{4,15}$'
            })
    )

    street = forms.CharField(
        label='Domicilio', required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'type': 'text',
                'placeholder': 'Av. del Libertador 256',
            })
    )

    remarks = forms.CharField(
        label='Domicilio', required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'type': 'text',
                'placeholder': 'Portones negros',
            })
    )

    town = forms.ModelChoiceField(
        label="Localidad", required=True,
        queryset=Town.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': 'required',
        }),
    )

    zipcode = forms.CharField(
        label='Código postal', required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'type': 'text',
                'placeholder': '1663',
                'pattern': r'^\d*$',
            })
    )

    max_delivery_date = forms.DateField(
        label='Fecha máxima de entrega', required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control datepicker',
                'placeholder': 'Fecha desde',
                'type': 'date',
            })
    )

    is_flex = forms.BooleanField(
        label='¿Es envío de Flex?', required=False,
        initial=False,
        widget=forms.CheckboxInput(
            attrs={
                'class': 'form-check-input',
                'type': 'checkbox',
            })
    )

    flex_id = forms.CharField(
        label='Tracking ID de Flex', required=False,
        widget=forms.TextInput(
            attrs={
                'type': 'text',
                'class': 'form-control',
                'placeholder': 'N° de ID',
                'disabled': 'disabled'
            }
        )
    )

    recipient_charge = forms.DecimalField(
        label='Cobrar al cliente', required=False,
    )

    deposit = forms.ModelChoiceField(
        label="Deposit",
        queryset=Deposit.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
    )

    class Meta:
        model = Envio
        fields = [
            'client',
            'detail',
            'name',
            'doc',
            'phone',
            'street',
            'remarks',
            'town',
            'zipcode',
            'charge',
            'max_delivery_date',
            'is_flex',
            'flex_id',
            'delivery_schedule',
            'deposit',
        ]
        widgets = {
            'delivery_schedule': forms.Select(attrs={
                'class': 'form-select',
            })
        }


class EnviosIdsSelection(forms.Form):
    ids = forms.CharField(
        label='Ids de envíos', required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'type': 'text',
                'placeholder': '1,2,3,4,5',
            })
    )
