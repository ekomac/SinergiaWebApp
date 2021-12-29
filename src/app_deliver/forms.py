from django import forms
from django.core.validators import FileExtensionValidator


class BulkLoadEnviosForm(forms.Form):
    file = forms.FileField(
        allow_empty_file=True,
        label="Si querés escanear alguna foto o archivo:",
        required=True,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
        }),
        validators=[FileExtensionValidator(
            ['pdf', 'xlsx', 'png', 'jpg', 'jpeg',
             'gif', 'doc', 'docx', 'xls', 'xlsx',
             'ppt', 'pptx', 'txt', 'csv', 'bmp',
             'tiff', 'tif', ]
        )])
