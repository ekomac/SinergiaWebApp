# Generated by Django 2.2.2 on 2022-04-10 18:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('changes', '0002_auto_20220410_1812'),
    ]

    operations = [
        migrations.AddField(
            model_name='change',
            name='labels',
            field=models.CharField(choices=[('IM', 'Mejora'), ('BF de error', 'Corrección de error'), ('UP', 'Actualización'), ('MC', 'Corrección menor'), ('WF', 'Sin solución')], default='I', max_length=2),
        ),
    ]
