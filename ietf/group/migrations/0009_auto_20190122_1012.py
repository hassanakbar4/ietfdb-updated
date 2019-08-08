# Copyright The IETF Trust 2019, All Rights Reserved
# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2019-01-22 10:12


from __future__ import absolute_import, print_function, unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0008_group_features_onetoone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalgroupfeatures',
            name='agenda_type',
            field=models.ForeignKey(blank=True, db_constraint=False, default='ietf', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='name.AgendaTypeName'),
        ),
    ]
