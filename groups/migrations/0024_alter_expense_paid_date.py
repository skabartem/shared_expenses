# Generated by Django 3.2.5 on 2021-10-12 20:37

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0023_auto_20211012_2236'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expense',
            name='paid_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 10, 12, 22, 37, 23, 371508), null=True),
        ),
    ]
