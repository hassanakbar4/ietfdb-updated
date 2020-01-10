# Copyright The IETF Trust 2020, All Rights Reserved
# -*- coding: utf-8 -*-
# Generated by Django 1.11.27 on 2020-01-07 09:25
from __future__ import unicode_literals

from django.db import migrations

def forward(apps, schema_editor):
    DBTemplate = apps.get_model('dbtemplate', 'DBTemplate')
    DBTemplate.objects.create(path='/nomcom/defaults/iesg_requirements', type_id='rst', title='Generic IESG requirements',
                              content="""=============================
IESG MEMBER DESIRED EXPERTISE
=============================

Place this year's Generic IESG Member Desired Expertise here.

This template uses reStructured text for formatting. Feel free to use it (to change the above header for example). 
""")

def reverse(apps, schema_editor):
    DBTemplate = apps.get_model('dbtemplate', 'DBTemplate')
    DBTemplate.objects.filter(path='/nomcom/defaults/iesg_requirements').delete()

class Migration(migrations.Migration):

    dependencies = [
        ('dbtemplate', '0007_adjust_review_assigned'),
    ]

    operations = [
        migrations.RunPython(forward, reverse)
    ]
