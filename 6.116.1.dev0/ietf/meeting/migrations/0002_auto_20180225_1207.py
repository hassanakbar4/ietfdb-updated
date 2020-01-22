# Copyright The IETF Trust 2018-2019, All Rights Reserved
# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-02-25 12:07


from __future__ import absolute_import, print_function, unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meeting', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='floorplan',
            options={'ordering': ['-id']},
        ),
        migrations.AlterModelOptions(
            name='importantdate',
            options={'ordering': ['-meeting_id', 'date']},
        ),
        migrations.AlterModelOptions(
            name='meeting',
            options={'ordering': ['-date', '-id']},
        ),
        migrations.AlterModelOptions(
            name='room',
            options={'ordering': ['-id']},
        ),
        migrations.AlterModelOptions(
            name='timeslot',
            options={'ordering': ['-time', '-id']},
        ),
        migrations.AlterField(
            model_name='floorplan',
            name='short',
            field=models.CharField(default='', max_length=3),
        ),
    ]
