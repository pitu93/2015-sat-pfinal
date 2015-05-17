# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Actividad',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('titulo', models.CharField(max_length=32)),
                ('tipo', models.CharField(max_length=32)),
                ('gratuito', models.IntegerField()),
                ('precio', models.IntegerField()),
                ('fecha', models.CharField(max_length=32)),
                ('hora', models.CharField(max_length=32)),
                ('duracion', models.IntegerField()),
                ('url', models.CharField(max_length=32)),
            ],
        ),
        migrations.CreateModel(
            name='Tabla',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user', models.CharField(max_length=32)),
                ('title', models.CharField(max_length=32)),
                ('descripcion', models.CharField(max_length=32)),
                ('actividad', models.CharField(max_length=32)),
            ],
        ),
    ]
