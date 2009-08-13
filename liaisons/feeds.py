# Copyright The IETF Trust 2007, All Rights Reserved

from django.contrib.syndication.feeds import Feed, FeedDoesNotExist
from django.utils.feedgenerator import Atom1Feed
from django.db.models import Q
from ietf.liaisons.models import LiaisonDetail, FromBodies
from ietf.idtracker.models import Acronym
import re

# A slightly funny feed class, the 'object' is really
# just a dict with some parameters that items() uses
# to construct a queryset.
class Liaisons(Feed):
    feed_type = Atom1Feed
    def get_object(self, bits):
	obj = {}
	if bits[0] == 'recent':
	    if len(bits) != 1:
		raise FeedDoesNotExist
	    obj['title'] = 'Recent Liaison Statements'
	    obj['limit'] = 15
	    return obj
	if bits[0] == 'from':
	    if len(bits) != 2:
		raise FeedDoesNotExist
	    try:
		acronym = Acronym.objects.get(acronym=bits[1])
		obj['filter'] = {'from_id': acronym.acronym_id}
		body = bits[1]
	    except Acronym.DoesNotExist:
		# Find body matches.  Turn all non-word characters
		# into wildcards for the like search.
		# Note that supplying sql here means that this is
		# mysql-specific (e.g., postgresql wants 'ilike' for
		# the same operation)
		body_list = FromBodies.objects.values('from_id','body_name').extra(where=['body_name like "%s"' % re.sub('\W', '_', bits[1])])
		if not body_list:
		    raise FeedDoesNotExist
		frmlist = [b['from_id'] for b in body_list]
		# Assume that all of the matches have the same name.
		# This is not guaranteed (e.g., a url like '-----------'
		# will match several bodies) but is true of well-formed
		# inputs.
		body = body_list[0]['body_name']
		obj['filter'] = {'from_id__in': frmlist}
	    obj['title'] = 'Liaison Statements from %s' % body
	    return obj
	if bits[0] == 'to':
	    if len(bits) != 2:
		raise FeedDoesNotExist
	    # The schema uses two different fields for the same
	    # basic purpose, depending on whether it's a Secretariat-submitted
	    # or Liaison-tool-submitted document.
	    obj['q'] = [ (Q(by_secretariat=0) & Q(to_body__icontains=bits[1])) | (Q(by_secretariat=1) & Q(submitter_name__icontains=bits[1])) ]
	    obj['title'] = 'Liaison Statements where to matches %s' % bits[1]
	    return obj
	if bits[0] == 'subject':
	    if len(bits) != 2:
		raise FeedDoesNotExist
	    obj['q'] = [ Q(title__icontains=bits[1]) | Q(uploads__file_title__icontains=bits[1]) ]
	    obj['title'] = 'Liaison Statements where subject matches %s' % bits[1]
	    return obj
	raise FeedDoesNotExist

    def get_feed(self, url=None):
        if not url:
            raise FeedDoesNotExist
        else:
            return Feed.get_feed(self, url=url)

    def title(self, obj):
	return obj['title']

    def link(self, obj):
	# no real equivalent for any objects
	return '/liaison/'

    def description(self, obj):
	return self.title(obj)

    def items(self, obj):
	# Start with the common queryset
	qs = LiaisonDetail.objects.all().order_by("-submitted_date")
	if obj.has_key('q'):
	    qs = qs.filter(*obj['q'])
	if obj.has_key('filter'):
	    qs = qs.filter(**obj['filter'])
	if obj.has_key('limit'):
	    qs = qs[:obj['limit']]
	return qs

    def item_pubdate(self, item):
	return item.submitted_date

    def item_author_name(self, item):
	return item.from_body()
