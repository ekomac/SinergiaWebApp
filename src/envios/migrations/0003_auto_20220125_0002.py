# Generated by Django 2.2.2 on 2022-01-25 00:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('envios', '0002_auto_20220124_2203'),
    ]

    operations = [
        migrations.AlterField(
            model_name='envio',
            name='carrier',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='envios_carried_by', to=settings.AUTH_USER_MODEL, verbose_name='Portador'),
        ),
        migrations.AlterField(
            model_name='envio',
            name='updated_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='envios_edited_by', to=settings.AUTH_USER_MODEL, verbose_name='Editado por'),
        ),
    ]
