# Copyright The IETF Trust 2020', 'All Rights Reserved
# -*- coding: utf-8 -*-
# Generated by Django 1.11.27 on 2020-02-12 07:11
from __future__ import unicode_literals

from django.db import migrations, models


def forward(apps, schema_editor):
    Group = apps.get_model('group', 'Group')
    initial_area_groups = ['dispatch', 'gendispatch', 'intarea', 'opsarea', 'opsawg', 'rtgarea', 'rtgwg', 'saag', 'secdispatch', 'tsvarea', 'irtfopen']
    Group.objects.filter(acronym__in=initial_area_groups).update(meeting_seen_as_area=True)
    

def reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0030_populate_default_used_roles'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='meeting_seen_as_area',
            field=models.BooleanField(default=False, help_text='For meeting scheduling, should be considered an area meeting, even if the type is WG'),
        ),
        migrations.AddField(
            model_name='grouphistory',
            name='meeting_seen_as_area',
            field=models.BooleanField(default=False, help_text='For meeting scheduling, should be considered an area meeting, even if the type is WG'),
        ),
        migrations.RunPython(forward, reverse),
    ]
