# Generated by Django 2.2.2 on 2022-04-06 18:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('envios', '0014_auto_20220406_1842'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bulkloadenvios',
            name='unused_flex_ids',
            field=models.TextField(blank=True, default=None, null=True, verbose_name='IDs de Flex no usados'),
        ),
    ]
