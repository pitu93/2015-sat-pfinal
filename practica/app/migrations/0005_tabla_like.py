# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_actividad_ide'),
    ]

    operations = [
        migrations.AddField(
            model_name='tabla',
            name='like',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
