# Copyright The IETF Trust 2020, All Rights Reserved
# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-03-19 13:06
from __future__ import unicode_literals

import re

import debug

from collections import OrderedDict

from django.db import migrations

name_map = {
    "Issue.*":                "tracker",
    ".*FAQ.*":                "faq",
    ".*Area Web Page":        "webpage",
    ".*Wiki":                 "wiki",
    "Home Page":              "webpage",
    "Slack.*":                "slack",
    "Additional .* Web Page": "webpage",
    "Additional .* Page":     "webpage",
    "Yang catalog entry.*":   "yc_entry",
    "Yang impact analysis.*": "yc_impact",
    "GitHub":                 "github_repo",
    "Github page":            "github_repo",
    "GitHub repo.*":          "github_repo",
    "Github repository.*":    "github_repo",
    "GitHub notifications":   "github_notify",
    "GitHub org.*":           "github_org",
    "GitHub User.*":          "github_username",
    "GitLab User":            "gitlab_username",
    "GitLab User Name":       "gitlab_username",
}

# TODO: Consider dropping known bad links at this point
#   " *https?://www.ietf.org/html.charters/*": None, # all these links are dead
#   " *http://www.bell-labs.com/mailing-lists/pint": None, # dead link
#   "http://www.ietf.org/wg/videos/mile-overview.html": None, # dead link
#   " http://domen.uninett.no/~hta/ietf/notary-status.h": None,  # dead link
#   " http://www.ERC.MsState.Edu/packetway": None, # dead link
#   "mailarchive\\.ietf\\.org" : None,
#   "bell-labs\\.com": None,
#   "html\\.charters": None,
#   "datatracker\\.ietf\\.org": None,
#   etc.

url_map = OrderedDict({
   "https?://github\\.com": "github_repo",
   "https?://trac\\.ietf\\.org/.*/wiki": "wiki",
   "ietf\\.org.*/trac/wiki": "wiki",
   "trac.*wiki": "wiki",
   "www\\.ietf\\.org/mailman" : "mailing_list",
   "www\\.ietf\\.org/mail-archive" : "mailing_list_archive",
   "ietf\\.org/logs": "jabber_log",
   "ietf\\.org/jabber/logs": "jabber_log",
   "xmpp:.*?join": "jabber_room",
   "https?://.*": "webpage"
})

def forward(apps, schema_editor):
    GroupExtResource = apps.get_model('group', 'GroupExtResource')
    ExtResourceName = apps.get_model('name', 'ExtResourceName')
    GroupUrl = apps.get_model('group', 'GroupUrl')

    mapped = 0
    not_mapped = 0
    ignored = 0

    debug.say("Matching...")
    for group_url in GroupUrl.objects.all():
        match_found = False
        for regext,slug in name_map.items():
            if re.match(regext, group_url.name):
                match_found = True
                mapped += 1
                name = ExtResourceName.objects.get(slug=slug)
                GroupExtResource.objects.create(group=group_url.group, name_id=slug, value=group_url.url, display_name=group_url.name) # TODO: validate this value against name.type
                break
        if not match_found:
            for regext, slug in url_map.items():
                group_url.url = group_url.url.strip()
                if re.search(regext, group_url.url):
                    match_found = True
                    if slug:
                        mapped +=1
                        name = ExtResourceName.objects.get(slug=slug)
                        # Munge the URL if it's the first github repo match
                        #  Remove "/tree/master" substring if it exists
                        #  Remove trailing "/issues" substring if it exists
                        #  Remove "/blob/master/.*" pattern if present
                        if regext == "https?://github\\.com":
                            group_url.url = group_url.url.replace("/tree/master","")
                            group_url.url = re.sub('/issues$', '', group_url.url)
                            group_url.url = re.sub('/blob/master.*$', '', group_url.url)
                        GroupExtResource.objects.create(group=group_url.group, name_id=slug, value=group_url.url, display_name=group_url.name) # TODO: validate this value against name.type
                    else:
                        ignored +=1
                    break
        if not match_found:
            debug.show('("Not Mapped:",group_url.group.acronym, group_url.name, group_url.url)')
            not_mapped += 1
    debug.show('(mapped, ignored, not_mapped)')

def reverse(apps, schema_editor):
    GroupExtResource = apps.get_model('group', 'GroupExtResource')
    GroupExtResource.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ('group', '0024_extres'),
        ('name', '0011_populate_extres'),
    ]

    operations = [
        migrations.RunPython(forward, reverse)
    ]
