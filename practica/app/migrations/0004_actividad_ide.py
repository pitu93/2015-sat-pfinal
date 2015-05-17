# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_auto_20150517_1359'),
    ]

    operations = [
        migrations.AddField(
            model_name='actividad',
            name='ide',
            field=models.CharField(default=0, max_length=32),
            preserve_default=False,
        ),
    ]
