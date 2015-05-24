# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_tabla_like'),
    ]

    operations = [
        migrations.CreateModel(
            name='Like',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('like', models.IntegerField()),
                ('actividad', models.CharField(max_length=32)),
            ],
        ),
        migrations.RemoveField(
            model_name='tabla',
            name='like',
        ),
    ]
