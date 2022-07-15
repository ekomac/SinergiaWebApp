import hashlib
from django import forms
from django.core.validators import FileExtensionValidator
from account.models import Account
from deposit.models import Deposit
from envios.bulkutil.exceptions import (
    InvalidExcelFileError, InvalidPdfFileError)
from envios.bulkutil.extractor import Extractor
from envios.models import BulkLoadEnvios, Envio
from clients.models import Client
from places.models import Town
from tracking.models import TrackingMovement
from tracking.utils.delivery import delivery_attempt
from tracking.utils.deposit import deposit_by_envios_tracking_ids
from tracking.utils.devolver import devolver_by_envios_tracking_ids
from tracking.utils.transfer import transfer_by_envios_tracking_ids
from tracking.utils.withdraw import withdraw_by_envios_tracking_ids


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
        bulk_load.original_file = self.cleaned_data.get('file')
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

    def clean_flex_id(self):
        flex_id = self.cleaned_data['flex_id']
        print('is_flex', self.cleaned_data['is_flex'])
        if (self.cleaned_data['is_flex'] and
                self.cleaned_data['is_flex'] is True):
            if not flex_id or len(flex_id) == 0:
                raise forms.ValidationError(
                    'El campo Tracking ID de Flex es obligatorio.')
            elif Envio.objects.filter(
                    flex_id=self.cleaned_data['flex_id']).exists():
                raise forms.ValidationError(
                    f'Ya existe un envío con el Tracking ID Flex #{flex_id}')
        return flex_id

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

    def clean_flex_id(self):
        print("Comprobando")
        flex_id = self.cleaned_data['flex_id']
        if self.instance:
            if self.instance.is_flex:
                if not flex_id or len(flex_id) == 0:
                    raise forms.ValidationError(
                        'El campo Tracking ID de Flex es obligatorio.')
                envios_with_id = Envio.objects.filter(
                    flex_id=self.cleaned_data['flex_id']
                ).exclude(pk=self.instance.pk)
                if envios_with_id.exists():
                    id_flex = 'Tracking ID Flex  #{}'.format(flex_id)
                    msg = f'Ya existe un envío con el {id_flex}'
                    raise forms.ValidationError(msg)
        return flex_id

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


class BaseActionForm(forms.Form):

    accept_risks = forms.BooleanField(
        label='Acepto los riesgos que implica esta operación',
        widget=forms.CheckboxInput(
            attrs={
                'class': 'form-check-input',
                'type': 'checkbox',
            })
    )

    def clean_accept_risks(self):
        accept_risks = self.cleaned_data['accept_risks']
        if accept_risks is False:
            raise forms.ValidationError(
                'Tenés que aceptar los riesgos para continuar.')
        return accept_risks

    def __init__(self, user: Account, envio: Envio, *args, **kwargs):
        self.user = user
        self.envio = envio
        super(BaseActionForm, self).__init__(*args, **kwargs)

    def perform_action(self) -> TrackingMovement:
        """Returns the tracking movement created by the action.

        Raises:
            NotImplementedError: If the action is not implemented.

        Returns:
            TrackingMovement: The tracking movement created by the action.
        """
        raise NotImplementedError("Subclass must implement perform_action()")


class CarrierModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.full_name_formal


class ActionWithdrawForm(BaseActionForm):

    to_carrier = CarrierModelChoiceField(
        label="Quién lo recibió", required=True,
        queryset=Account.objects.filter(
            groups__name__in=['Admins', 'Level 1', 'Level 2']
        ).order_by('last_name'),
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
    )

    def perform_action(self) -> TrackingMovement:
        return withdraw_by_envios_tracking_ids(
            self.user,
            self.envio.deposit,
            self.cleaned_data['to_carrier'],
            self.envio.tracking_id)


class ActionDepositForm(BaseActionForm):

    to_deposit = forms.ModelChoiceField(
        label="Deposit", required=True,
        queryset=Deposit.objects.filter(client__isnull=True),
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
    )

    def perform_action(self) -> TrackingMovement:
        return deposit_by_envios_tracking_ids(
            self.user,
            self.envio.carrier,
            self.cleaned_data['to_deposit'],
            self.envio.tracking_id)


class ActionTransferForm(BaseActionForm):

    to_carrier = CarrierModelChoiceField(
        label="Quién lo recibió", required=True,
        queryset=Account.objects.filter(
            groups__name__in=['Admins', 'Level 1', 'Level 2']
        ).order_by('last_name'),
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
    )

    def perform_action(self) -> TrackingMovement:
        return transfer_by_envios_tracking_ids(
            self.user,
            self.envio.carrier,
            self.cleaned_data['to_carrier'],
            self.envio.tracking_id)


class ActionDevolverForm(BaseActionForm):

    to_deposit = forms.ModelChoiceField(
        label="Deposit", required=True,
        queryset=Deposit.objects.none(),
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
    )

    def __init__(self, user: Account, envio: Envio, *args, **kwargs):
        super().__init__(user, envio, *args, **kwargs)
        self.fields['to_deposit'].queryset = Deposit.objects.filter(
            client=self.envio.client)

    def perform_action(self) -> TrackingMovement:
        return devolver_by_envios_tracking_ids(
            self.user,
            self.envio.carrier,
            self.cleaned_data['to_deposit'],
            self.envio.tracking_id)


class ActionDeliveryAttemptForm(BaseActionForm):

    result = forms.ChoiceField(
        label='Motivo de no entrega', required=True,
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
        choices=(
            (TrackingMovement.RESULT_REJECTED_AT_DESTINATION,
             'Rechazado en lugar de destino'),
            (TrackingMovement.RESULT_REPROGRAMED, 'Reprogramado'),
            (TrackingMovement.RESULT_NO_ANSWER, 'Sin respuesta'),
            (TrackingMovement.RESULT_OTHER, 'Otro'),
        )
    )

    comment = forms.CharField(
        label='Comentarios', required=False,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'type': 'text',
                'placeholder': 'Motivo de no entrega',
            })
    )

    proof = forms.ImageField(
        label='Comprobante de entrega', required=False,
        widget=forms.FileInput(
            attrs={
                'class': 'form-control',
                'type': 'file',
            })
    )

    def perform_action(self) -> TrackingMovement:
        author = self.user
        result = self.cleaned_data['result']
        envio_tracking_id = self.envio.tracking_id
        proof = self.cleaned_data.get('proof', None)
        comment = self.cleaned_data.get('comment', "")
        movement = TrackingMovement(
            created_by=author,
            from_carrier=author,
            action=TrackingMovement.ACTION_DELIVERY_ATTEMPT,
            result=result,
            proof=proof,
            comment=comment,
        )
        movement.save()

        envio = Envio.objects.filter(tracking_id=envio_tracking_id).first()

        # Add envios to the movement
        movement.envios.add(envio)

        envio.has_delivery_attempt = True
        envio.save()

        return movement


class ActionSuccessfulDeliveryForm(BaseActionForm):

    receiver_doc_id = forms.CharField(
        label='DNI del destinatario', required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'type': 'text',
                'placeholder': '12345678',
                'pattern': r'^\d{8}$'
            })
    )

    comment = forms.CharField(
        label='Comentarios', required=False,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'type': 'text',
                'placeholder': 'Motivo de no entrega',
            })
    )

    def perform_action(self) -> TrackingMovement:
        movement, _ = delivery_attempt(
            author=self.user,
            result_obtained=TrackingMovement.RESULT_DELIVERED,
            envio_tracking_id=self.envio.tracking_id,
            receiver_doc_id=self.cleaned_data['receiver_doc_id']
        )
        if comment := self.cleaned_data.get('comment', None):
            movement.comment = comment
            movement.save()
        return movement
