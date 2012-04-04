# Copyright The IETF Trust 2011, All Rights Reserved

from django.conf.urls.defaults import patterns, url
from ietf.doc.models import State

urlpatterns = patterns('django.views.generic.simple',
    url(r'^help/state/$', 'direct_to_template', { 'template': 'wgcharter/states.html', 'extra_context': { 'states': State.objects.filter(type="charter") } }, name='help_charter_states'),
)
urlpatterns += patterns('',
    url(r'^(?P<name>[A-Za-z0-9._+-]+)/edit/state/$', "ietf.wgcharter.views.change_state", name='wg_change_state'),
    url(r'^(?P<name>[A-Za-z0-9._+-]+)/edit/(?P<option>initcharter|recharter|abandon)/$', "ietf.wgcharter.views.change_state", name='wg_startstop_process'),
    url(r'^(?P<name>[A-Za-z0-9._+-]+)/edit/telechat/$', "ietf.wgcharter.views.telechat_date", name='charter_telechat_date'),
    url(r'^(?P<name>[A-Za-z0-9._+-]+)/edit/(?P<ann>action|review)/$', "ietf.wgcharter.views.announcement_text", name='wg_announcement_text'),
    url(r'^(?P<name>[A-Za-z0-9._+-]+)/edit/ballotwriteupnotes/$', "ietf.wgcharter.views.ballot_writeupnotes", name='wg_ballot_writeupnotes'),
    url(r'^(?P<name>[A-Za-z0-9._+-]+)/edit/approveballot/$', "ietf.wgcharter.views.approve_ballot", name='wg_approve_ballot'),
    url(r'^(?P<name>[A-Za-z0-9._+-]+)/submit/$', "ietf.wgcharter.views.submit", name='wg_submit'),

)
