# Generated by Django 3.2.5 on 2021-10-13 10:21

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0026_auto_20211012_2240'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='text',
            field=models.CharField(default='New expense was added', max_length=100),
        ),
        migrations.AlterField(
            model_name='expense',
            name='paid_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 10, 13, 12, 21, 17, 524487), null=True),
        ),
    ]