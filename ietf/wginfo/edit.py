# edit/create view for WGs

import re, os, string, datetime

from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django import forms
from django.utils import simplejson

from ietf.ietfauth.decorators import role_required, has_role

from ietf.doc.models import *
from ietf.name.models import *
from ietf.person.models import *
from ietf.group.models import *
from ietf.group.utils import save_group_in_history
from ietf.wgcharter.utils import set_or_create_charter
from ietf.wgcharter.mails import email_secretariat
from ietf.person.forms import EmailsField


class WGForm(forms.Form):
    name = forms.CharField(max_length=255, label="WG Name", required=True)
    acronym = forms.CharField(max_length=8, label="WG Acronym", required=True)
    chairs = EmailsField(label="WG Chairs", required=False)
    secretaries = EmailsField(label="WG Secretaries", required=False)
    techadv = EmailsField(label="WG Technical Advisors", required=False)
    ad = forms.ModelChoiceField(Person.objects.filter(role__name="ad", role__group__state="active").order_by('name'), label="Shepherding AD", empty_label="(None)", required=False)
    parent = forms.ModelChoiceField(Group.objects.filter(type="area", state="active").order_by('name'), label="IETF Area", empty_label="(None)", required=False)
    list_email = forms.CharField(max_length=64, required=False)
    list_subscribe = forms.CharField(max_length=255, required=False)
    list_archive = forms.CharField(max_length=255, required=False)
    urls = forms.CharField(widget=forms.Textarea, label="Additional URLs", help_text="Format: http://site/path (Optional description). Separate multiple entries with newline.", required=False)

    def __init__(self, *args, **kwargs):
        self.cur_acronym = kwargs.pop('cur_acronym')
        self.hide = kwargs.pop('hide', None)
        super(self.__class__, self).__init__(*args, **kwargs)

        # hide requested fields
        if self.hide:
            for f in self.hide:
                self.fields[f].widget = forms.HiddenInput

        # if previous AD is now ex-AD, append that person to the list
        ad_pk = self.initial.get('ad')
        choices = self.fields['ad'].choices
        if ad_pk and ad_pk not in [pk for pk, name in choices]:
            self.fields['ad'].choices = list(choices) + [("", "-------"), (ad_pk, Person.objects.get(pk=ad_pk).plain_name())]

    def clean_acronym(self):
        acronym = self.cleaned_data['acronym']
        if self.cur_acronym and acronym != self.cur_acronym:
            if Group.objects.filter(acronym__iexact=acronym):
                raise forms.ValidationError("Acronym used in an existing WG. Please pick another.")
            if GroupHistory.objects.filter(acronym__iexact=acronym):
                raise forms.ValidationError("Acronym used in a previous WG. Please pick another.")
        return acronym

    def clean_urls(self):
        return [x.strip() for x in self.cleaned_data["urls"].splitlines() if x.strip()]

def format_urls(urls, fs="\n"):
    res = []
    for u in urls:
        if u.name:
            res.append(u"%s (%s)" % (u.url, u.name))
        else:
            res.append(u.url)
    return fs.join(res)
        
@role_required('Area Director', 'Secretariat')
def edit(request, acronym=None, action="edit"):
    """Edit or create a WG, notifying parties as
    necessary and logging changes as group events."""
    if action == "edit":
        # Editing. Get group
        wg = get_object_or_404(Group, acronym=acronym)
        charter = set_or_create_charter(wg)
        new_wg = False
    elif action == "create":
        wg = None
        new_wg = True
    else:
        raise Http404()

    login = request.user.get_profile()

    if request.method == 'POST':
        form = WGForm(request.POST, cur_acronym=wg.acronym if wg else None)
        if form.is_valid():
            r = form.cleaned_data
            if not new_wg:
                gh = save_group_in_history(wg)
            else:
                # Create WG
                wg = Group(name=r["name"],
                           acronym=r["acronym"],
                           type=GroupTypeName.objects.get(name="WG"),
                           state=GroupStateName.objects.get(name="Proposed"))
                wg.save()
                
                e = ChangeStateGroupEvent(group=wg, type="changed_state")
                e.time = datetime.datetime.now()
                e.by = login
                e.state_id = "proposed"
                e.desc = "Proposed group"
                e.save()

            if not wg.charter:
                # Create adjoined charter
                charter = set_or_create_charter(wg)
                charter.set_state(State.objects.get(type="charter", slug="infrev"))
                charter.save()
                
                e = DocEvent(doc=charter, type="started_iesg_process")
                e.time = datetime.datetime.now()
                e.by = login
                e.desc = "Started IESG process on charter"
                e.save()
                
            changes = []
                
            def desc(attr, new, old):
                entry = "%(attr)s changed to <b>%(new)s</b> from %(old)s"
                if new_wg:
                    entry = "%(attr)s changed to <b>%(new)s</b>"
                    
                return entry % dict(attr=attr, new=new, old=old)

            def diff(attr, name):
                v = getattr(wg, attr)
                if r[attr] != v:
                    changes.append(desc(name, r[attr], v))
                    setattr(wg, attr, r[attr])
                    if attr == "acronym":
                        c = wg.charter
                        save_document_in_history(c)
                        # and add a DocAlias
                        DocAlias.objects.create(
                            name = "charter-ietf-%s" % r['acronym'],
                            document = charter
                            )

            # update the attributes, keeping track of what we're doing
            diff('name', "Name")
            diff('acronym', "Acronym")
            diff('ad', "Shepherding AD")
            diff('parent', "IETF Area")
            diff('list_email', "Mailing list email")
            diff('list_subscribe', "Mailing list subscribe address")
            diff('list_archive', "Mailing list archive")
            
            # update roles
            for attr, slug, title in [('chairs', 'chair', "Chairs"), ('secretaries', 'secr', "Secretaries"), ('techadv', 'techadv', "Tech Advisors")]:
                new = r[attr]
                old = Email.objects.filter(role__group=wg, role__name=slug).select_related("person")
                if set(new) != set(old):
                    changes.append(desc(title,
                                        ", ".join(x.get_name() for x in new),
                                        ", ".join(x.get_name() for x in old)))
                    wg.role_set.filter(name=slug).delete()
                    for e in new:
                        Role.objects.get_or_create(name_id=slug, email=e, group=wg, person=e.person)

            # update urls
            new_urls = r['urls']
            old_urls = format_urls(wg.groupurl_set.order_by('url'), ", ")
            if ", ".join(sorted(new_urls)) != old_urls:
                changes.append(desc('Urls', ", ".join(sorted(new_urls)), old_urls))
                wg.groupurl_set.all().delete()
                # Add new ones
                for u in new_urls:
                    m = re.search('(?P<url>[\w\d:#@%/;$()~_?\+-=\\\.&]+)( \((?P<name>.+)\))?', u)
                    if m:
                        if m.group('name'):
                            url = GroupURL(url=m.group('url'), name=m.group('name'), group=wg)
                        else:
                            url = GroupURL(url=m.group('url'), name='', group=wg)
                        url.save()

            wg.time = datetime.datetime.now()

            if changes and not new_wg:
                for c in changes:
                    GroupEvent.objects.create(group=wg, by=login, type="info_changed", desc=c)

            wg.save()

            if new_wg:
                return redirect('wg_startstop_process', name=wg.acronym, option="initcharter")

            return redirect('wg_charter', acronym=wg.acronym)
    else: # form.is_valid()
        if not new_wg:
            from ietf.person.forms import json_emails
            init = dict(name=wg.name,
                        acronym=wg.acronym,
                        chairs=Email.objects.filter(role__group=wg, role__name="chair"),
                        secretaries=Email.objects.filter(role__group=wg, role__name="secr"),
                        techadv=Email.objects.filter(role__group=wg, role__name="techadv"),
                        charter=wg.charter.name if wg.charter else None,
                        ad=wg.ad_id if wg.ad else None,
                        parent=wg.parent.id if wg.parent else None,
                        list_email=wg.list_email if wg.list_email else None,
                        list_subscribe=wg.list_subscribe if wg.list_subscribe else None,
                        list_archive=wg.list_archive if wg.list_archive else None,
                        urls=format_urls(wg.groupurl_set.all()),
                        )
            hide = None
        else:
            init = dict(ad=login.id if has_role(request.user, "Area Director") else None,
                        )
            hide = ['chairs', 'techadv', 'list_email', 'list_subscribe', 'list_archive', 'urls']
        form = WGForm(initial=init, cur_acronym=wg.acronym if wg else None, hide=hide)

    return render_to_response('wginfo/edit.html',
                              dict(wg=wg,
                                   form=form,
                                   user=request.user,
                                   login=login),
                              context_instance=RequestContext(request))



class ConcludeForm(forms.Form):
    instructions = forms.CharField(widget=forms.Textarea, required=True)

@role_required('Area Director','Secretariat')
def conclude(request, acronym):
    """Request the closing of a WG, prompting for instructions."""
    try:
        wg = Group.objects.get(acronym=acronym)
    except Group.DoesNotExist:
        wglist = GroupHistory.objects.filter(acronym=acronym)
        if wglist:
            return redirect('wg_conclude', acronym=wglist[0].group.acronym)
        else:
            raise Http404

    login = request.user.get_profile()

    if request.method == 'POST':
        form = ConcludeForm(request.POST)
        if form.is_valid():
            instructions = form.cleaned_data['instructions']

            email_secretariat(request, wg, "conclude", instructions)

            return redirect('wg_charter', acronym=wg.acronym)
    else:
        form = ConcludeForm()

    return render_to_response('wginfo/conclude.html',
                              dict(form=form,
                                   wg=wg),
                              context_instance=RequestContext(request))
