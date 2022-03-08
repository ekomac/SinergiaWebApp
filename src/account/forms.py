import re
from django import forms
from account.models import Account
from django.contrib.auth import authenticate

from clients.models import Client

ERROR_INVALID_EMAIL = "El email no existe."
PASSWORD_RESET_ERROR_DATA_NOT_RECEIVED = (
    "No se recibieron los datos de la contraseña.")
PASSWORD_RESET_ERROR_PASSWORDS_DONT_MATCH = (
    "Las contraseñas no coinciden.")
PASSWORD_RESET_ERROR_AT_LEAST_EIGHT_CHARS = (
    "La contraseña debe tener al menos 8 caracteres.")
PASSWORD_RESET_ERROR_MAX_TWENTY_CHARS = (
    "La contraseña debe tener menos de 20 caracteres.")
PASSWORD_RESET_ERROR_MUST_CONTAIN_MAYUS = (
    "La contraseña debe tener al menos una mayúscula.")
PASSWORD_RESET_ERROR_MUST_CONTAIN_MINUS = (
    "La contraseña debe tener al menos una minúscula.")
PASSWORD_RESET_ERROR_MUST_CONTAIN_NUM = (
    "La contraseña debe tener al menos un número.")
PASSWORD_RESET_ERROR_MUST_CONTAIN_SPECIAL = (
    "La contraseña debe tener al menos un caracter especial: '@#$%&*.,'")


class AccountAuthenticationForm(forms.ModelForm):

    password = forms.CharField(label="Constraseña", widget=forms.PasswordInput)
    email = forms.CharField(label="Correo electrónico",
                            widget=forms.EmailInput)

    class Meta:
        model = Account
        fields = ('email', 'password')

    def clean(self):
        email = self.cleaned_data.get('email', None)
        password = self.cleaned_data.get('password', None)
        email_ok = email is not None
        pass_ok = password is not None
        if email_ok and pass_ok and not authenticate(
                email=email, password=password):
            raise forms.ValidationError('Credenciales inválidas.')


class PasswordResetForm(forms.Form):

    email = forms.EmailField(
        label='Correo electrónico', widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
                'type': 'email',
            })
    )

    password = forms.CharField(
        label='Contraseña', widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'type': 'password',
            })
    )

    password_confirm = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'type': 'password',
            })
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        if not Account.objects.filter(email=email).exists():
            raise forms.ValidationError(ERROR_INVALID_EMAIL)
        return email

    def clean_password(self):
        password = self.cleaned_data['password']
        print(password)
        if len(password) < 8:
            raise forms.ValidationError(
                PASSWORD_RESET_ERROR_AT_LEAST_EIGHT_CHARS)
        elif len(password) > 20:
            raise forms.ValidationError(PASSWORD_RESET_ERROR_MAX_TWENTY_CHARS)
        elif not re.search(r'[A-Z]', password):
            raise forms.ValidationError(
                PASSWORD_RESET_ERROR_MUST_CONTAIN_MAYUS)
        elif not re.search(r'[a-z]', password):
            raise forms.ValidationError(
                PASSWORD_RESET_ERROR_MUST_CONTAIN_MINUS)
        elif not re.search(r'[0-9]', password):
            raise forms.ValidationError(PASSWORD_RESET_ERROR_MUST_CONTAIN_NUM)
        elif not re.search(r'[@#$%&*.,]', password):
            raise forms.ValidationError(
                PASSWORD_RESET_ERROR_MUST_CONTAIN_SPECIAL)
        return password

    def clean_password_confirm(self):
        password_1 = self.cleaned_data.get('password')
        password_2 = self.cleaned_data.get('password_confirm')
        if password_1 != password_2:
            raise forms.ValidationError(
                PASSWORD_RESET_ERROR_PASSWORDS_DONT_MATCH)
        return password_2

    def save(self, commit=True):
        cleaned_data = super().clean()
        email = cleaned_data.get('email', None)
        password = cleaned_data.get('password', None)
        if email is None or password is None:
            raise forms.ValidationError(PASSWORD_RESET_ERROR_DATA_NOT_RECEIVED)
        else:
            account = Account.objects.get(email=email)
            account.set_password(password)
            account.has_to_reset_password = False
            if commit:
                account.save()
                return account
            else:
                return account


class CreateAccountForm(forms.ModelForm):

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={'class': 'form-control', 'type': 'email'}),
        required=True,
    )

    username = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'type': 'text', 'maxlength': '40'}
        ),
        required=True,
    )

    profile_picture = forms.ImageField(
        widget=forms.FileInput(
            attrs={'class': 'form-control', 'type': 'file'}
        ),
        required=False,
    )

    client = forms.ModelChoiceField(
        queryset=Client.objects.all(),
        widget=forms.Select(
            # attrs={'class': 'form-select', }
        ),
        required=False,
    )

    first_name = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'type': 'text', 'maxlength': '30'}
        ),
        required=True,
    )

    last_name = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'type': 'text', 'maxlength': '30'}
        ),
        required=True,
    )

    date_of_birth = forms.DateField(
        widget=forms.DateInput(
            attrs={'class': 'form-control', 'type': 'date'}
        ),
        required=True,
    )

    phone = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'type': 'text', 'maxlength': '20'}
        ),
        required=False,
    )

    dni = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'type': 'text', 'maxlength': '8'}
        ),
        required=False,
    )

    address = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'type': 'text', 'maxlength': '100'}
        ),
        required=False,
    )

    dni_img = forms.FileField(
        widget=forms.FileInput(
            attrs={'class': 'form-control', 'type': 'file'}
        ),
        required=False,
    )

    role = forms.ChoiceField(
        choices=Account.ROLES,
        widget=forms.Select(
            attrs={'class': 'form-select', }
        ),
        required=True,
    )

    driver_license = forms.FileField(
        widget=forms.FileInput(
            attrs={'class': 'form-control', 'type': 'file'}
        ),
        required=False,
    )

    criminal_record = forms.FileField(
        widget=forms.FileInput(
            attrs={'class': 'form-control', 'type': 'file'}
        ),
        required=False,
    )

    vtv = forms.FileField(
        widget=forms.FileInput(
            attrs={'class': 'form-control', 'type': 'file'}
        ),
        required=False,
    )

    insurance = forms.FileField(
        widget=forms.FileInput(
            attrs={'class': 'form-control', 'type': 'file'}
        ),
        required=False,
    )

    cedula = forms.FileField(
        widget=forms.FileInput(
            attrs={'class': 'form-control', 'type': 'file'}
        ),
        required=False,
    )

    vehicle_type = forms.ChoiceField(
        choices=Account.VEHICLES,
        widget=forms.Select(
            attrs={'class': 'form-select'}
        ),
        required=False)

    vehicle_id = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'type': 'text', 'maxlength': '20'}
        ),
        required=False,
    )

    class Meta:
        model = Account
        fields = (
            'email',
            'username',
            'profile_picture',
            'role',
            'client',
            'first_name',
            'last_name',
            'date_of_birth',
            'phone',
            'dni',
            'address',
            'dni_img',
            'driver_license',
            'criminal_record',
            'vtv',
            'insurance',
            'cedula',
            'vehicle_type',
            'vehicle_id',

        )

    def clean_client(self):
        client = self.cleaned_data.get('client', '')
        role = self.cleaned_data.get('role', '')
        print("Cleaning client. Role=", role, "client=", client)
        if client in [None, ''] and role == "client":
            raise forms.ValidationError(
                ("Si el rol es 'cliente', tenés que seleccionar \
                    un cliente de referencia."))
        return client


class UpdateAccountForm(CreateAccountForm):

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={'class': 'form-control', 'type': 'email'}),
        required=True,
    )

    username = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'type': 'text', 'maxlength': '40'}
        ),
        required=True,
    )

    profile_picture = forms.ImageField(
        widget=forms.FileInput(
            attrs={'class': 'form-control', 'type': 'file'}
        ),
        required=False,
    )

    client = forms.ModelChoiceField(
        queryset=Client.objects.all(),
        widget=forms.Select(
            # attrs={'class': 'form-select', }
        ),
        required=False,
    )

    first_name = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'type': 'text', 'maxlength': '30'}
        ),
        required=True,
    )

    last_name = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'type': 'text', 'maxlength': '30'}
        ),
        required=True,
    )

    date_of_birth = forms.DateField(
        widget=forms.DateInput(
            attrs={'class': 'form-control', 'type': 'date'}
        ),
        required=True,
    )

    phone = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'type': 'text', 'maxlength': '20'}
        ),
        required=False,
    )

    dni = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'type': 'text', 'maxlength': '8'}
        ),
        required=False,
    )

    address = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'type': 'text', 'maxlength': '100'}
        ),
        required=False,
    )

    dni_img = forms.FileField(
        widget=forms.FileInput(
            attrs={'class': 'form-control', 'type': 'file'}
        ),
        required=False,
    )

    role = forms.ChoiceField(
        choices=Account.ROLES,
        widget=forms.Select(
            attrs={'class': 'form-select', }
        ),
        required=True,
    )

    driver_license = forms.FileField(
        widget=forms.FileInput(
            attrs={'class': 'form-control', 'type': 'file'}
        ),
        required=False,
    )

    criminal_record = forms.FileField(
        widget=forms.FileInput(
            attrs={'class': 'form-control', 'type': 'file'}
        ),
        required=False,
    )

    vtv = forms.FileField(
        widget=forms.FileInput(
            attrs={'class': 'form-control', 'type': 'file'}
        ),
        required=False,
    )

    insurance = forms.FileField(
        widget=forms.FileInput(
            attrs={'class': 'form-control', 'type': 'file'}
        ),
        required=False,
    )

    cedula = forms.FileField(
        widget=forms.FileInput(
            attrs={'class': 'form-control', 'type': 'file'}
        ),
        required=False,
    )

    vehicle_type = forms.ChoiceField(
        choices=Account.VEHICLES,
        widget=forms.Select(
            attrs={'class': 'form-select'}
        ),
        required=False)

    vehicle_id = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'type': 'text', 'maxlength': '20'}
        ),
        required=False,
    )

    clean_previous_profile_picture = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(
            attrs={'class': 'form-check-input', }),
        initial=False,
    )

    clean_previous_dni_img = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(
            attrs={'class': 'form-check-input', }),
        initial=False,
    )

    clean_previous_driver_license = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(
            attrs={'class': 'form-check-input', }),
        initial=False,
    )

    clean_previous_criminal_record = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(
            attrs={'class': 'form-check-input', }),
        initial=False,
    )

    clean_previous_vtv = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(
            attrs={'class': 'form-check-input', }),
        initial=False,
    )

    clean_previous_insurance = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(
            attrs={'class': 'form-check-input', }),
        initial=False,
    )

    clean_previous_cedula = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(
            attrs={'class': 'form-check-input', }),
        initial=False,
    )

    class Meta:
        model = Account
        fields = (
            'email',
            'username',
            'profile_picture',
            'role',
            'client',
            'first_name',
            'last_name',
            'date_of_birth',
            'phone',
            'dni',
            'address',
            'dni_img',
            'driver_license',
            'criminal_record',
            'vtv',
            'insurance',
            'cedula',
            'vehicle_type',
            'vehicle_id',

        )

    def save(self, commit=True):
        """Save the account"""
        account = super(UpdateAccountForm, self).save(commit=False)
        self.delete_files_if_needed()
        if commit:
            account.save()
        return account

    def clean_client(self):
        client = self.cleaned_data.get('client', '')
        role = self.cleaned_data.get('role', '')
        print("Cleaning client. Role=", role, "client=", client)
        if client in [None, ''] and role == "client":
            raise forms.ValidationError(
                ("Si el rol es 'cliente', tenés que seleccionar \
                    un cliente de referencia."))
        return client

    def delete_files_if_needed(self):
        """Delete the file if needed"""
        profile_picture = self.cleaned_data['clean_previous_profile_picture']
        if 'profile_picture' not in self.changed_data and profile_picture:
            self.instance.profile_picture.delete(False)
        dni_img = self.cleaned_data['clean_previous_dni_img']
        if 'dni_img' not in self.changed_data and dni_img:
            self.instance.dni_img.delete(False)
        driver_license = self.cleaned_data['clean_previous_driver_license']
        if 'driver_license' not in self.changed_data and driver_license:
            self.instance.driver_license.delete(False)
        criminal_record = self.cleaned_data['clean_previous_criminal_record']
        if 'criminal_record' not in self.changed_data and criminal_record:
            self.instance.criminal_record.delete(False)
        vtv = self.cleaned_data['clean_previous_vtv']
        if 'vtv' not in self.changed_data and vtv:
            self.instance.vtv.delete(False)
        insurance = self.cleaned_data['clean_previous_insurance']
        if 'insurance' not in self.changed_data and insurance:
            self.instance.insurance.delete(False)
        cedula = self.cleaned_data['clean_previous_cedula']
        if 'cedula' not in self.changed_data and cedula:
            self.instance.cedula.delete(False)
