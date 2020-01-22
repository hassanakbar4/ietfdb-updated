# Copyright The IETF Trust 2019, All Rights Reserved
# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2019-11-19 02:41
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion
import ietf.utils.models


class Migration(migrations.Migration):

    dependencies = [
        ('person', '0009_auto_20190118_0725'),
        ('name', '0007_fix_m2m_slug_id_length'),
        ('meeting', '0021_rename_meeting_agenda_to_schedule'),
    ]

    operations = [
        migrations.CreateModel(
            name='SchedulingEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(default=datetime.datetime.now, help_text='When the event happened')),
                ('by', ietf.utils.models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='person.Person')),
                ('session', ietf.utils.models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='meeting.Session')),
                ('status', ietf.utils.models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='name.SessionStatusName')),
            ],
        ),
    ]
