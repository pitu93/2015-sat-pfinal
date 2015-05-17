# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_actividad_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='actividad',
            name='gratuito',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='actividad',
            name='precio',
            field=models.IntegerField(null=True),
        ),
    ]
