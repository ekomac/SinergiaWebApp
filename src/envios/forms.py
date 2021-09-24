from django import forms
from envios.models import Envio


class CreateEnvioForm(forms.ModelForm):

    class Meta:
        model = Envio
        fields = ['detail', 'client', 'recipient_name', 'recipient_doc',
                  'recipient_phone', 'recipient_address',
                  'recipient_entrances', 'recipient_town',
                  'recipient_zipcode', 'recipient_charge', 'max_delivery_date',
                  'is_flex', 'flex_id', 'delivery_schedule',
                  ]

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
