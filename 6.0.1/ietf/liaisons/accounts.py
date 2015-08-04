from itertools import chain

from ietf.ietfauth.utils import has_role
from ietf.person.models import Person
from ietf.group.models import Role

def proxy_personify_role(role):
    """Return person from role with an old-school email() method using
    email from role."""
    p = role.person
    p.email = lambda: (p.plain_name(), role.email.address)
    return p



"""
def get_ietf_chair():
    try:
        return Role.objects.get(name="chair", group__acronym="ietf")
    except Role.DoesNotExist:
        return None


def get_iesg_chair():
    return get_ietf_chair()


def get_iab_chair():
    try:
        return Role.objects.get(name="chair", group__acronym="iab")
    except Role.DoesNotExist:
        return None


def get_irtf_chair():
    try:
        return Role.objects.get(name="chair", group__acronym="irtf")
    except Role.DoesNotExist:
        return None


def get_iab_executive_director():
    try:
        return Role.objects.get(name="execdir", group__acronym="iab")
    except Role.DoesNotExist:
        return None

def get_person_for_user(user):
    if not user.is_authenticated():
        return None
    try:
        p = user.person
        p.email = lambda: (p.plain_name(), p.email_address())
        return p
    except Person.DoesNotExist:
        return None

def is_areadirector(person):
    return bool(Role.objects.filter(person=person, name="ad", group__state="active", group__type="area"))


def is_wgchair(person):
    return bool(Role.objects.filter(person=person, name="chair", group__state="active", group__type="wg"))


def is_wgsecretary(person):
    return bool(Role.objects.filter(person=person, name="secr", group__state="active", group__type="wg"))


def is_ietfchair(person):
    return bool(Role.objects.filter(person=person, name="chair", group__acronym="ietf"))


def is_iabchair(person):
    return bool(Role.objects.filter(person=person, name="chair", group__acronym="iab"))


def is_iab_executive_director(person):
    return bool(Role.objects.filter(person=person, name="execdir", group__acronym="iab"))


def is_irtfchair(person):
    return bool(Role.objects.filter(person=person, name="chair", group__acronym="irtf"))
    
def is_sdo_liaison_manager(person):
    return bool(Role.objects.filter(person=person, name="liaiman", group__type="sdo"))


def is_sdo_authorized_individual(person):
    return bool(Role.objects.filter(person=person, name="auth", group__type="sdo"))


def is_secretariat(user):
    if isinstance(user, basestring):
        return False
    return user.is_authenticated() and bool(Role.objects.filter(person__user=user, name="secr", group__acronym="secretariat"))


def is_sdo_manager_for_outgoing_liaison(person, liaison):
    if liaison.from_group and liaison.from_group.type_id == "sdo":
        return bool(liaison.from_group.role_set.filter(name="liaiman", person=person))
    return False


def is_sdo_manager_for_incoming_liaison(person, liaison):
    if liaison.to_group and liaison.to_group.type_id == "sdo":
        return bool(liaison.to_group.role_set.filter(name="liaiman", person=person))
    return False


def can_edit_liaison(user, liaison):
    if is_secretariat(user):
        return True
    person = get_person_for_user(user)
    if is_sdo_liaison_manager(person):
        return (is_sdo_manager_for_outgoing_liaison(person, liaison) or
                is_sdo_manager_for_incoming_liaison(person, liaison))
    return False
"""

