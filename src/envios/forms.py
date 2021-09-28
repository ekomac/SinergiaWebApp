from django import forms
from envios.models import Envio
from clients.models import Client


class CreateEnvioForm(forms.ModelForm):
    detail = forms.CharField(label='Detalle', required=True,
                             id="details",
                             widget=forms.TextInput(attrs={
                                 'class': 'form-control',
                                 'type': 'text',
                             }),)

    client = forms.ModelChoiceField(
        label='Producto', required=True,
        queryset=Client.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
    )

    class Meta:
        model = Envio
        fields = ['detail', 'client', 'recipient_name', 'recipient_doc',
                  'recipient_phone', 'recipient_address',
                  'recipient_entrances', 'recipient_town',
                  'recipient_zipcode', 'recipient_charge', 'max_delivery_date',
                  'is_flex', 'flex_id', 'delivery_schedule',
                  ]

    # customer_last_name = forms.CharField(label='Apellido', required=False,
    #                                      widget=forms.TextInput(attrs={
    #                                          'class': 'form-control',
    #                                          'type': 'text',
    #                                      }))
    # customer_email = forms.EmailField(label='Email', required=False,
    #                                   widget=forms.EmailInput(attrs={
    #                                       'class': 'form-control',
    #                                       'placeholder': 'nombre@ejemplo.com',
    #                                   }))
    # customer_tel = forms.CharField(label='Teléfono', required=False,
    #                                widget=forms.TextInput(attrs={
    #                                    'class': 'form-control',
    #                                    'placeholder': '+54 11 1234-5678',
    #                                    'pattern': '^\\d{6,17}$'
    #                                }))
    # customer_city = forms.CharField(label='Localidad', required=False,
    #                                 widget=forms.TextInput(attrs={
    #                                     'class': 'form-control',
    #                                     'placeholder': 'Bella Vista',
    #                                 }))
    # customer_zip_code = forms.CharField(label='CP', required=False,
    #                                     widget=forms.TextInput(attrs={
    #                                         'class': 'form-control',
    #                                         'placeholder': '1661',
    #                                         'pattern': '^\\d{4,7}$'
    #                                     }))
    # customer_state = forms.CharField(label='Provincia', required=False,
    #                                  widget=forms.TextInput(attrs={
    #                                      'class': 'form-control',
    #                                      'placeholder': 'Buenos Aires',
    #                                      'value': 'Buenos Aires',
    #                                  }))
    # discount = forms.CharField(label='Descuento confección', required=True,
    #                            widget=forms.TextInput(attrs={
    #                                'class': 'form-control',
    #                                'type': 'number',
    #                                'min': '0.00',
    #                                'value': '0',
    #                                'step': '0.01',
    #                            }))

    # def save(self, commit=True):
    # envio = self.instance
    # envio.detail = self.cleaned_data['detail']
    # envio.client = self.cleaned_data['client']
    # envio.recipient_name = self.cleaned_data['recipient_name']
    # envio.recipient_doc = self.cleaned_data['recipient_doc']
    # envio.recipient_phone = self.cleaned_data['recipient_phone']
    # envio.recipient_address = self.cleaned_data['recipient_address']
    # envio.recipient_entrances = self.cleaned_data['recipient_entrances']
    # envio.recipient_town = self.cleaned_data['recipient_town']
    # envio.recipient_zipcode = self.cleaned_data['recipient_zipcode']
    # envio.recipient_charge = self.cleaned_data['recipient_charge']
    # envio.max_delivery_date = self.cleaned_data['max_delivery_date']
    # envio.is_flex = self.cleaned_data['is_flex']
    # envio.flex_id = self.cleaned_data['flex_id']
    # envio.delivery_schedule = self.cleaned_data['delivery_schedule']

    # if self.cleaned_data['image']:
        #   blog_post.image = self.cleaned_data['image']
    #     user1.pic.save('abc.png', File(open('/tmp/pic.png', 'r')))
    # if commit:
    #     envio.save()
    # envio.save()
    # qr = qrcode.make(f'{envio.id}')
    # qr = qrcode.make(f'{envio.id}')
    # return blog_post
