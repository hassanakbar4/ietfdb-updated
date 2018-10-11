# Autogenerated by the mkresources management command 2014-11-13 23:53
from ietf.api import ModelResource
from ietf.api import ToOneField
from tastypie.fields import ToManyField
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.cache import SimpleCache

from ietf import api

from ietf.message.models import Message, SendQueue, MessageAttachment, AnnouncementFrom
from ietf.person.resources import PersonResource
from ietf.group.resources import GroupResource
from ietf.doc.resources import DocumentResource

class MessageResource(ModelResource):
    by               = ToOneField(PersonResource, 'by')
    related_groups   = ToManyField(GroupResource, 'related_groups', null=True)
    related_docs     = ToManyField(DocumentResource, 'related_docs', null=True)
    class Meta:
        cache = SimpleCache()
        queryset = Message.objects.all()
        serializer = api.Serializer()
        #resource_name = 'message'
        filtering = { 
            "id": ALL,
            "time": ALL,
            "subject": ALL,
            "frm": ALL,
            "to": ALL,
            "cc": ALL,
            "bcc": ALL,
            "reply_to": ALL,
            "body": ALL,
            "content_type": ALL,
            "by": ALL_WITH_RELATIONS,
            "related_groups": ALL_WITH_RELATIONS,
            "related_docs": ALL_WITH_RELATIONS,
        }
api.message.register(MessageResource())

from ietf.person.resources import PersonResource
class SendQueueResource(ModelResource):
    by               = ToOneField(PersonResource, 'by')
    message          = ToOneField(MessageResource, 'message')
    class Meta:
        cache = SimpleCache()
        queryset = SendQueue.objects.all()
        serializer = api.Serializer()
        #resource_name = 'sendqueue'
        filtering = { 
            "id": ALL,
            "time": ALL,
            "send_at": ALL,
            "sent_at": ALL,
            "note": ALL,
            "by": ALL_WITH_RELATIONS,
            "message": ALL_WITH_RELATIONS,
        }
api.message.register(SendQueueResource())



class MessageAttachmentResource(ModelResource):
    message          = ToOneField(MessageResource, 'message')
    class Meta:
        queryset = MessageAttachment.objects.all()
        serializer = api.Serializer()
        cache = SimpleCache()
        #resource_name = 'messageattachment'
        filtering = { 
            "id": ALL,
            "filename": ALL,
            "removed": ALL,
            "body": ALL,
            "message": ALL_WITH_RELATIONS,
        }
api.message.register(MessageAttachmentResource())



from ietf.group.resources import GroupResource
from ietf.name.resources import RoleNameResource
class AnnouncementFromResource(ModelResource):
    name             = ToOneField(RoleNameResource, 'name')
    group            = ToOneField(GroupResource, 'group')
    class Meta:
        queryset = AnnouncementFrom.objects.all()
        serializer = api.Serializer()
        cache = SimpleCache()
        #resource_name = 'announcementfrom'
        filtering = { 
            "id": ALL,
            "address": ALL,
            "name": ALL_WITH_RELATIONS,
            "group": ALL_WITH_RELATIONS,
        }
api.message.register(AnnouncementFromResource())
