from django import forms
from account.models import Account
from django.contrib.auth import authenticate


class AccountAuthenticationForm(forms.ModelForm):

    password = forms.CharField(label="Constraseña", widget=forms.PasswordInput)

    class Meta:
        model = Account
        fields = ('email', 'password')

    def clean(self):
        email = self.cleaned_data['email']
        password = self.cleaned_data['password']
        if not authenticate(email=email, password=password):
            raise forms.ValidationError('Credenciales inválidas.')
