# Copyright The IETF Trust 2007, All Rights Reserved

from django.conf.urls.defaults import patterns, url
from ietf.liaisons.models import LiaisonDetail

info_dict = {
    'queryset': LiaisonDetail.objects.all().order_by("-submitted_date"),
}

# there's an opportunity for date-based filtering.
urlpatterns = patterns('django.views.generic.list_detail',
     url(r'^$', 'object_list', info_dict, name='liaison_list'),
     (r'^(?P<object_id>\d+)/$', 'object_detail', info_dict),
)

urlpatterns += patterns('django.views.generic.simple',
     (r'^help/$', 'direct_to_template', {'template': 'liaisons/help.html'}),
     (r'^help/fields/$', 'direct_to_template', {'template': 'liaisons/field_help.html'}),
     (r'^help/from_ietf/$', 'direct_to_template', {'template': 'liaisons/guide_from_ietf.html'}),
     (r'^help/to_ietf/$', 'direct_to_template', {'template': 'liaisons/guide_to_ietf.html'}),
     (r'^managers/$', 'redirect_to', { 'url': 'http://www.ietf.org/liaison/managers.html' })
)

urlpatterns += patterns('ietf.liaisons.views',
     url(r'^add/$', 'add_liaison', name='add_liaison'),
     url(r'^ajax/get_poc_for_incoming/$', 'get_poc_for_incoming', name='get_poc_for_incoming'),
     url(r'^ajax/get_cc_for_incoming/$', 'get_cc_for_incoming', name='get_cc_for_incoming'),
)
