import hashlib
from typing import List
from django import forms
from django.core.validators import FileExtensionValidator
from account.models import Account
from envios.bulkutil.exceptions import (
    InvalidExcelFileError, InvalidPdfFileError)
from envios.bulkutil.extractor import Extractor
from envios.models import BulkLoadEnvios, Envio
from clients.models import Client
from envios.utils import NoSuggestionsAvailable, town_resolver
from places.models import Town


class MissingColumn(Exception):
    pass


class MissingTown(Exception):
    pass


class BulkLoadEnviosForm(forms.ModelForm):

    client = forms.ModelChoiceField(
        label="Cliente", required=True,
        queryset=Client.objects.all(),
        widget=forms.Select(attrs={
            'class': ' form-select',
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
        self.file_contet = None
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
        bulk_load.hashed_file = self.hash_from_file
        # If a bulk_load with same hash and not finished
        #  is found, delete it before saving this
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
        bulk_load.csv_result = self.result
        bulk_load.errors = self.found_errors
        bulk_load.requires_manual_fix = self.requires_manual_fix
        bulk_load.cells_to_paint = self.cells_to_paint
        if commit:
            bulk_load.save()
        return bulk_load


class BulkAddForm(forms.Form):

    def __init__(self, user=None, *args, **kwargs):
        super(BulkAddForm, self).__init__(*args, **kwargs)
        self.result = None
        self.csv_file = None
        self.author = user
        self.csv_result = None
        self.csv_result_error_rowcols = []
        self.csv_result_no_suggestions = False

    client = forms.ModelChoiceField(
        label="Cliente", required=True,
        queryset=Client.objects.all(),
        widget=forms.Select(attrs={
            'class': ' form-select',
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

    accept_changes = forms.BooleanField(
        label="Aceptar cambios", required=False, initial=False)

    def save(self):
        Envio.objects.bulk_create(self.result)
        return True

    def clean_file(self):
        file = self.cleaned_data.get('file')
        return file

    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get('file')
        client = cleaned_data.get('client')
        use_suggestions = cleaned_data.get('accept_changes')
        if file and client:
            extractor = Extractor()
            self.csv_result, _ = extractor.get_shipments(file)
            self.result = self.get_envios_from_csv(
                self.csv_result, self.author, client, use_suggestions)

    def get_envios_from_csv(
        self, csv_str: str, author: Account,
            client: Client, use_suggestions: bool = False) -> List[Envio]:
        """[summary]

        Args:
            csv_str (str): [description]
            author (Account): [description]
            client (Client): [description]

        Raises:
            forms.ValidationError: [description]

        Returns:
            List[Envio]: [description]
        """
        envios = []
        errors = []
        for i, row in enumerate(csv_str.split("\n")):
            if i == 0 or "traking_id" in row:
                continue
            cols = row.split(",")
            kwargs = {}

            domicilio = None
            if not cols[1]:
                self.csv_result_error_rowcols.append(f"{i+1},2")
                self.csv_result_no_suggestions = True
                errors.append(
                    forms.ValidationError(
                        f"En la fila {i+1}, columna 2 no \
                            se especificó el domicilio \
                                ({cols[1]}, {cols[3]} {cols[4]})."
                    )
                )
            else:
                domicilio = cols[1]

            if not cols[4]:
                self.csv_result_no_suggestions = True
                self.csv_result_error_rowcols.append(f"{i+1},5")
                error = forms.ValidationError(
                    f"En la fila {i+1}, columna 5, no se \
                        especificó la localidad ({cols[1]}, \
                            {cols[3]} {cols[4]}).")
                errors.append(error)

            towns = Town.objects.filter(name=cols[4].upper())
            town = None
            if not towns or len(towns) > 1:
                self.csv_result_error_rowcols.append(f"{i+1},5")
                try:
                    result, reason = town_resolver(cols[4], cols[5], cols[3])
                    if use_suggestions:
                        town = result
                    else:
                        errors.append(forms.ValidationError(
                            f'En la fila {i+1}, columna 5, no se encontró \
                                la localidad con el nombre {cols[4]} \
                                    ({cols[1]}, {cols[3]} {cols[4]}). ¿Acaso \
                                    quisiste decir {result}? {reason}'
                        ))
                except NoSuggestionsAvailable:
                    self.csv_result_no_suggestions = True
                    errors.append(forms.ValidationError(
                        f'En la fila {i+1}, columna 5, no se encontró \
                            la localidad con el nombre {cols[4]} \
                                (({cols[1]}, {cols[3]} {cols[4]})), y no \
                                    tenemos sugerencias para vos.'
                    ))
            else:
                town = towns[0]

            # Flex code related
            if cols[0]:
                kwargs['is_flex'] = True
                kwargs['flex_id'] = cols[0]

            # Adress
            kwargs['recipient_address'] = domicilio
            # Entrances
            kwargs['recipient_entrances'] = cols[2] if cols[2] else None
            # Zipcode
            kwargs['recipient_zipcode'] = cols[3] if cols[3] else None
            # Town
            kwargs['recipient_town'] = town
            # Recipient's Name
            kwargs['recipient_name'] = cols[6] if cols[6] else None
            # Recipient's Doc Id
            kwargs['recipient_doc'] = cols[7] if cols[7] else None
            # Recipient's Phone
            kwargs['recipient_phone'] = cols[8] if cols[8] else None
            # Detail (packages)
            kwargs['detail'] = cols[9] if cols[9] else "0-1"

            kwargs['created_by'] = author
            kwargs['client'] = client

            envios.append(Envio(**kwargs))
        if errors:
            raise forms.ValidationError(errors)
        return envios

    def get_csv_result(self):
        errors = ""
        if self.csv_result_error_rowcols:
            errors = "-".join(self.csv_result_error_rowcols)
        return (self.csv_result, errors, self.csv_result_no_suggestions)


class CreateEnvioForm(forms.ModelForm):
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

    recipient_name = forms.CharField(
        label='Nombre del destinatario', required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'type': 'text',
                'placeholder': 'Juan Pérez',
            }),
    )

    recipient_doc = forms.CharField(
        label='DNI', required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'type': 'text',
                'placeholder': '30.123.567',
                'pattern': r'^\d{7,8}$',
            }),
    )

    recipient_phone = forms.CharField(
        label='Teléfono', required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'type': 'text',
                'placeholder': '11 1234-5678',
                'pattern': r'^\d{4,15}$'
            })
    )

    recipient_address = forms.CharField(
        label='Domicilio', required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'type': 'text',
                'placeholder': 'Av. del Libertador 256',
            })
    )

    recipient_entrances = forms.CharField(
        label='Domicilio', required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'type': 'text',
                'placeholder': 'Portones negros',
            })
    )

    recipient_town = forms.ModelChoiceField(
        label="Localidad", required=True,
        queryset=Town.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': 'required',
        }),
    )

    recipient_zipcode = forms.CharField(
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
        model = Envio
        fields = [
            'client',
            'detail',
            'recipient_name',
            'recipient_doc',
            'recipient_phone',
            'recipient_address',
            'recipient_entrances',
            'recipient_town',
            'recipient_zipcode',
            'recipient_charge',
            'max_delivery_date',
            'is_flex',
            'flex_id',
            'delivery_schedule',
        ]
        widgets = {
            'delivery_schedule': forms.Select(attrs={
                'class': 'form-select',
            })
        }
