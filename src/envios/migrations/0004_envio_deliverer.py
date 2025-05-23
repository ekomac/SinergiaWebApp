# Generated by Django 2.2.2 on 2022-01-26 18:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('envios', '0003_auto_20220125_0002'),
    ]

    operations = [
        migrations.AddField(
            model_name='envio',
            name='deliverer',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='envios_delivered_by', to=settings.AUTH_USER_MODEL, verbose_name='Quién lo entregó'),
        ),
    ]
