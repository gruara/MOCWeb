# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-07 20:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MOCapi', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tracks',
            name='track_name',
            field=models.CharField(max_length=30, null=True),
        ),
    ]
