# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-03-25 11:37
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smartpanel', '0004_auto_20180318_1649'),
    ]

    operations = [
        migrations.AddField(
            model_name='layout',
            name='version',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='layout',
            name='version_date',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2018, 3, 1, 0, 0, 0)),
            preserve_default=False,
        ),
    ]
