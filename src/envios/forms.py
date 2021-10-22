from typing import List
from django import forms
from account.models import Account
from envios.bulkutil.extractor import Extractor
from envios.models import Envio
from clients.models import Client
from places.models import Town
from rich import print


class MissingColumn(Exception):
    pass


class MissingTown(Exception):
    pass


class BulkAddForm(forms.Form):

    def __init__(self, user=None, *args, **kwargs):
        super(BulkAddForm, self).__init__(*args, **kwargs)
        self.result = None
        self.csv_file = None
        self.author = user

    client = forms.ModelChoiceField(
        label="Cliente", required=True,
        queryset=Client.objects.all(),
        widget=forms.Select(attrs={
            'class': ' form-select',
        }),
    )

    file = forms.FileField(allow_empty_file=False,
                           label="Archivo", required=True)

    def save(self):
        Envio.objects.bulk_create(self.result)
        return True

    def clean_file(self):
        print("cleaning file")
        file = self.cleaned_data.get('file')
        return file

    def clean(self):
        print("[red]cleaning file[red]")
        cleaned_data = super().clean()
        file = cleaned_data.get('file')
        client = cleaned_data.get('client')
        if file and client:
            extractor = Extractor()
            self.csv_result, _ = extractor.get_shipments(file)
            self.result = self.get_envios_from_csv(
                self.csv_result, self.author, client)
        # if errors:
        #     raise forms.ValidationError(errors)
        # return value

    def get_envios_from_csv(
        self, csv_str: str, author: Account,
            client: Client) -> List[Envio]:
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
                print("acá debemos pasar")
                continue
            print("estamos en", i)
            cols = row.split(",")
            kwargs = {}

            if not cols[1]:
                # errors.append(
                errors.append(
                    forms.ValidationError(
                        f"En la fila {i}, columna 1 no \
                            se especificó el domicilio."
                    )
                )

            if not cols[4]:
                error = forms.ValidationError(
                    f"En la fila {i}, columna no se especificó la localidad.")
                errors.append(error)

            # Town
            towns = Town.objects.filter(name=cols[4].upper())
            print(towns)
            if not towns:
                error = forms.ValidationError(
                    f"En la fila {i}, columna 4, no se encontró \
                        la localidad con el nombre {cols[4]}")
                errors.append(error)
            elif len(towns) > 1:
                towns = Town.objects.filter(
                    name=cols[4].upper(), partido__name=cols[5].upper())
                if not towns:
                    error = forms.ValidationError(
                        f"En la fila {i}, columna 4, se indicó una localidad que \
                            pertenece a más de un partido. Tratamos de \
                                especificar una con el partido {cols[5]}, \
                                    pero este partido no se encontró.")
                    errors.append(error)

            if errors:
                raise forms.ValidationError(errors)

            # Flex code related
            if cols[0]:
                kwargs['is_flex'] = True
                kwargs['flex_id'] = cols[0]

            # Adress
            kwargs['recipient_address'] = cols[1]
            # Entrances
            kwargs['recipient_entrances'] = cols[2] if cols[2] else None
            # Zipcode
            kwargs['recipient_zipcode'] = cols[3] if cols[3] else None
            # Town
            kwargs['recipient_town'] = towns[0]
            # Recipient's Name
            kwargs['recipient_name'] = cols[6] if cols[6] else None
            # Recipient's Doc Id
            kwargs['recipient_doc'] = cols[7] if cols[7] else None
            # Recipient's Phone
            kwargs['recipient_phone'] = cols[8] if cols[8] else None
            # Detail (packages)
            if cols[9]:
                kwargs['detail'] = cols[9]

            kwargs['created_by'] = author
            kwargs['client'] = client

            envios.append(Envio(**kwargs))

        return envios

    def get_csv_result(self):
        return self.csv_result


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
