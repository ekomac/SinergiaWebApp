from django import forms
from account.models import Account
from django.contrib.auth import authenticate


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
