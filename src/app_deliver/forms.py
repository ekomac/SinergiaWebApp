from django import forms
from django.core.validators import FileExtensionValidator


class DeliverForm(forms.Form):
    proof = forms.FileField(
        allow_empty_file=True,
        label="Si querés escanear alguna foto o archivo:",
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
        }),
        validators=[FileExtensionValidator(
            ['pdf', 'xlsx', 'png', 'jpg', 'jpeg',
             'gif', 'doc', 'docx', 'xls', 'xlsx',
             'ppt', 'pptx', 'txt', 'csv', 'bmp',
             'tiff', 'tif', ]
        )])
    result = forms.CharField(label="Resultado")
    eid = forms.CharField(label="Envio id")
    comment = forms.CharField(label="Comentario", required=False)
