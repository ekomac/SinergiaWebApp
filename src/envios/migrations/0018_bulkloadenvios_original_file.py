# Generated by Django 2.2.2 on 2022-07-15 18:09

from django.db import migrations, models
import envios.models


class Migration(migrations.Migration):

    dependencies = [
        ('envios', '0017_envio_has_delivery_attempt'),
    ]

    operations = [
        migrations.AddField(
            model_name='bulkloadenvios',
            name='original_file',
            field=models.FileField(blank=True, null=True, upload_to=envios.models.bulk_file_upload_path, verbose_name='Archivo original'),
        ),
    ]
