# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-05-24 08:25
from __future__ import unicode_literals

from django.db import migrations, models

def forward(apps, schema_editor):
    TopicAudienceName = apps.get_model('name','TopicAudienceName')
    # """General, Nominee, Nomcom Member"""
    TopicAudienceName.objects.create(
        slug='general',
        name='General',
        desc='Anyone who can log in',
    )
    TopicAudienceName.objects.create(
        slug='nominees',
        name='Nominees',
        desc='Anyone who has accepted a Nomination for an open position',
    )
    TopicAudienceName.objects.create(
        slug='nomcom',
        name='Nomcom Members',
        desc='Members of this nomcom',
    )

def reverse(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('name', '0019_add_docrelationshipname_downref_approval'),
    ]

    operations = [
        migrations.CreateModel(
            name='TopicAudienceName',
            fields=[
                ('slug', models.CharField(max_length=32, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('desc', models.TextField(blank=True)),
                ('used', models.BooleanField(default=True)),
                ('order', models.IntegerField(default=0)),
            ],
            options={
                'ordering': ['order', 'name'],
                'abstract': False,
            },
        ),
        migrations.RunPython(forward,reverse),
    ]
