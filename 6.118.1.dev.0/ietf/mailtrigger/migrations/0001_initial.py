# Copyright The IETF Trust 2018-2019, All Rights Reserved
# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-02-20 10:52


from __future__ import absolute_import, print_function, unicode_literals

import six
if six.PY3:
    from typing import List, Tuple      # pyflakes:ignore

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]                                   # type: List[Tuple[str]]

    operations = [
        migrations.CreateModel(
            name='MailTrigger',
            fields=[
                ('slug', models.CharField(max_length=32, primary_key=True, serialize=False)),
                ('desc', models.TextField(blank=True)),
            ],
            options={
                'ordering': ['slug'],
            },
        ),
        migrations.CreateModel(
            name='Recipient',
            fields=[
                ('slug', models.CharField(max_length=32, primary_key=True, serialize=False)),
                ('desc', models.TextField(blank=True)),
                ('template', models.TextField(blank=True, null=True)),
            ],
            options={
                'ordering': ['slug'],
            },
        ),
        migrations.AddField(
            model_name='mailtrigger',
            name='cc',
            field=models.ManyToManyField(blank=True, related_name='used_in_cc', to='mailtrigger.Recipient'),
        ),
        migrations.AddField(
            model_name='mailtrigger',
            name='to',
            field=models.ManyToManyField(blank=True, related_name='used_in_to', to='mailtrigger.Recipient'),
        ),
    ]
