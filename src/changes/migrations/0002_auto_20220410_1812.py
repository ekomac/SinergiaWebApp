# Generated by Django 2.2.2 on 2022-04-10 18:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('changes', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='change',
            options={'verbose_name': 'Cambio', 'verbose_name_plural': 'Cambios'},
        ),
        migrations.RenameField(
            model_name='change',
            old_name='date',
            new_name='date_created',
        ),
    ]
