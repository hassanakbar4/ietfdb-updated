# Copyright The IETF Trust 2007, All Rights Reserved

#import models
import datetime
import os
import re
import tarfile

from tempfile import mkstemp

from django import forms
from django.shortcuts import render_to_response, get_object_or_404
from django.utils import simplejson as json
from ietf.idtracker.models import IETFWG, IRTF, Area
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.template import RequestContext
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.decorators import decorator_from_middleware
from ietf.ietfauth.decorators import group_required, has_role
from django.middleware.gzip import GZipMiddleware
from django.db.models import Max
from django.forms.models import modelform_factory
from django.forms import ModelForm

import debug
import urllib

from ietf.utils.pipe import pipe
from ietf.doc.models import Document, State

# Old model -- needs to be removed
from ietf.proceedings.models import Meeting as OldMeeting, WgMeetingSession, Proceeding, Switches

# New models
from ietf.person.models  import Person
from ietf.meeting.models import TimeSlot, Session, Schedule, Room
from ietf.group.models import Group

from ietf.meeting.helpers import agenda_info
from ietf.meeting.helpers import get_areas
from ietf.meeting.helpers import build_all_agenda_slices, get_wg_name_list
from ietf.meeting.helpers import get_scheduledsessions_from_schedule, get_all_scheduledsessions_from_schedule
from ietf.meeting.helpers import get_modified_from_scheduledsessions
from ietf.meeting.helpers import get_wg_list, find_ads_for_meeting
from ietf.meeting.helpers import get_meeting, get_schedule, agenda_permissions

import debug

@decorator_from_middleware(GZipMiddleware)
def materials(request, meeting_num=None):
    proceeding = get_object_or_404(Proceeding, meeting_num=meeting_num)
    begin_date = proceeding.sub_begin_date
    cut_off_date = proceeding.sub_cut_off_date
    cor_cut_off_date = proceeding.c_sub_cut_off_date
    now = datetime.date.today()
    if settings.SERVER_MODE != 'production' and '_testoverride' in request.REQUEST:
        pass
    elif now > cor_cut_off_date:
        return render_to_response("meeting/materials_upload_closed.html",{'meeting_num':meeting_num,'begin_date':begin_date, 'cut_off_date':cut_off_date, 'cor_cut_off_date':cor_cut_off_date}, context_instance=RequestContext(request))
    sub_began = 0
    if now > begin_date:
        sub_began = 1
    #sessions  = Session.objects.filter(meeting__number=meeting_num, timeslot__isnull=False)
    meeting = get_meeting(meeting_num)
    schedule = get_schedule(meeting,None )
    sessions  = Session.objects.filter(meeting__number=meeting_num,scheduledsession__schedule=schedule ).select_related()
    plenaries = sessions.filter(name__icontains='plenary')
    ietf      = sessions.filter(group__parent__type__slug = 'area').exclude(group__acronym='edu')
    irtf      = sessions.filter(group__parent__acronym = 'irtf')
    training  = sessions.filter(group__acronym__in=['edu','iaoc'])
    iab       = sessions.filter(group__parent__acronym = 'iab')

    cache_version = Document.objects.filter(session__meeting__number=meeting_num).aggregate(Max('time'))["time__max"]
    #
    return render_to_response("meeting/materials.html",
                              {'meeting_num':meeting_num,
                               'plenaries': plenaries, 'ietf':ietf, 'training':training, 'irtf': irtf, 'iab':iab,
                               'begin_date':begin_date, 'cut_off_date':cut_off_date,
                               'cor_cut_off_date':cor_cut_off_date,'sub_began':sub_began,
                               'cache_version':cache_version},
                              context_instance=RequestContext(request))

def current_materials(request):
    meeting = OldMeeting.objects.exclude(number__startswith='interim-').order_by('-meeting_num')[0]
    return HttpResponseRedirect( reverse(materials, args=[meeting.meeting_num]) )

def get_user_agent(request):
    if  settings.SERVER_MODE != 'production' and '_testiphone' in request.REQUEST:
        user_agent = "iPhone"
    elif 'user_agent' in request.REQUEST:
        user_agent = request.REQUEST['user_agent']
    elif 'HTTP_USER_AGENT' in request.META:
        user_agent = request.META["HTTP_USER_AGENT"]
    else:
        user_agent = ""
    return user_agent

class SaveAsForm(forms.Form):
    savename = forms.CharField(max_length=100)

@group_required('Area Director','Secretariat')
def agenda_create(request, num=None, name=None):
    meeting = get_meeting(num)
    schedule = get_schedule(meeting, name)

    if schedule is None:
        # here we have to return some ajax to display an error.
        raise Http404("No meeting information for meeting %s schedule %s available" % (num,name))

    # authorization was enforced by the @group_require decorator above.

    saveasform = SaveAsForm(request.POST)
    if not saveasform.is_valid():
        return HttpResponse(status=404)

    savedname = saveasform.cleaned_data['savename']

    # create the new schedule, and copy the scheduledsessions
    try:
        sched = meeting.schedule_set.get(name=savedname, owner=request.user.person)
        if sched:
            # XXX needs to record a session error and redirect to where?
            return HttpResponseRedirect(
                reverse(edit_agenda,
                        args=[meeting.number, sched.name]))

    except Schedule.DoesNotExist:
        pass

    # must be done
    newschedule = Schedule(name=savedname,
                           owner=request.user.person,
                           meeting=meeting,
                           visible=False,
                           public=False)

    newschedule.save()
    if newschedule is None:
        return HttpResponse(status=500)

    # keep a mapping so that extendedfrom references can be chased.
    mapping = {};
    for ss in schedule.scheduledsession_set.all():
        # hack to copy the object, creating a new one
        # just reset the key, and save it again.
        oldid = ss.pk
        ss.pk = None
        ss.schedule=newschedule
        ss.save()
        mapping[oldid] = ss.pk
        #print "Copying %u to %u" % (oldid, ss.pk)

    # now fix up any extendedfrom references to new set.
    for ss in newschedule.scheduledsession_set.all():
        if ss.extendedfrom is not None:
            oldid = ss.extendedfrom.id
            newid = mapping[oldid]
            #print "Fixing %u to %u" % (oldid, newid)
            ss.extendedfrom = newschedule.scheduledsession_set.get(pk = newid)
            ss.save()


    # now redirect to this new schedule.
    return HttpResponseRedirect(
        reverse(edit_agenda,
                args=[meeting.number, newschedule.name]))


@group_required('Secretariat')
@decorator_from_middleware(GZipMiddleware)
def edit_timeslots(request, num=None):

    meeting = get_meeting(num)
    timeslots = meeting.timeslot_set.exclude(location__isnull = True).all()

    time_slices,date_slices,slots = meeting.build_timeslices()

    meeting_base_url = request.build_absolute_uri(meeting.base_url())
    site_base_url = request.build_absolute_uri('/')[:-1] # skip the trailing slash

    rooms = meeting.room_set.order_by("capacity")
    rooms = rooms.all()

    # this import locate here to break cyclic loop.
    from ietf.meeting.ajax import timeslot_roomsurl, AddRoomForm, timeslot_slotsurl, AddSlotForm
    roomsurl  =reverse(timeslot_roomsurl, args=[meeting.number])
    adddayurl =reverse(timeslot_slotsurl, args=[meeting.number])

    return HttpResponse(render_to_string("meeting/timeslot_edit.html",
                                         {"timeslots": timeslots,
                                          "meeting_base_url": meeting_base_url,
                                          "site_base_url": site_base_url,
                                          "rooms":rooms,
                                          "addroom":  AddRoomForm(),
                                          "roomsurl": roomsurl,
                                          "addday":   AddSlotForm(),
                                          "adddayurl":adddayurl,
                                          "time_slices":time_slices,
                                          "slot_slices": slots,
                                          "date_slices":date_slices,
                                          "meeting":meeting},
                                         RequestContext(request)), mimetype="text/html")

class RoomForm(ModelForm):
    class Meta:
        model = Room
        exclude = ('meeting',)

@group_required('Secretariat')
def edit_roomurl(request, num, roomid):
    meeting = get_meeting(num)

    try:
        room = meeting.room_set.get(pk=roomid)
    except Room.DoesNotExist:
        raise Http404("No room %u for meeting %s" % (roomid, meeting.name))

    if request.POST:
        roomform = RoomForm(request.POST)
        new_room = roomform.save(commit=False)
        new_room.meeting = meeting
        new_room.save()
        roomform.save_m2m()
        return HttpResponseRedirect( reverse(edit_timeslots, args=[meeting.number]) )

    roomform = RoomForm(instance=room)
    meeting_base_url = request.build_absolute_uri(meeting.base_url())
    site_base_url = request.build_absolute_uri('/')[:-1] # skip the trailing slash
    return HttpResponse(render_to_string("meeting/room_edit.html",
                                         {"meeting_base_url": meeting_base_url,
                                          "site_base_url": site_base_url,
                                          "editroom":  roomform,
                                          "meeting":meeting},
                                         RequestContext(request)), mimetype="text/html")

##############################################################################
#@group_required('Area Director','Secretariat')
# disable the above security for now, check it below.
@decorator_from_middleware(GZipMiddleware)
def edit_agenda(request, num=None, name=None):

    if request.method == 'POST':
        return agenda_create(request, num, name)

    user  = request.user
    requestor = "AnonymousUser"
    if not user.is_anonymous():
        #print "user: %s" % (user)
        try:
            requestor = user.get_profile()
        except Person.DoesNotExist:
            # if we can not find them, leave them alone, only used for debugging.
            pass

    meeting = get_meeting(num)
    #sys.stdout.write("requestor: %s for sched_name: %s \n" % ( requestor, name ))
    schedule = get_schedule(meeting, name)
    #sys.stdout.write("2 requestor: %u for sched owned by: %u \n" % ( requestor.id, schedule.owner.id ))

    meeting_base_url = request.build_absolute_uri(meeting.base_url())
    site_base_url = request.build_absolute_uri('/')[:-1] # skip the trailing slash

    rooms = meeting.room_set.order_by("capacity")
    rooms = rooms.all()
    saveas = SaveAsForm()
    saveasurl=reverse(edit_agenda,
                      args=[meeting.number, schedule.name])

    cansee,canedit = agenda_permissions(meeting, schedule, user)

    if not cansee:
        #sys.stdout.write("visible: %s public: %s owner: %s request from: %s\n" % (
        #        schedule.visible, schedule.public, schedule.owner, requestor))
        return HttpResponse(render_to_string("meeting/private_agenda.html",
                                             {"schedule":schedule,
                                              "meeting": meeting,
                                              "meeting_base_url":meeting_base_url},
                                             RequestContext(request)), status=403, mimetype="text/html")

    scheduledsessions = get_all_scheduledsessions_from_schedule(schedule)

    # get_modified_from needs the query set, not the list
    modified = get_modified_from_scheduledsessions(scheduledsessions)

    area_list = get_areas()
    wg_name_list = get_wg_name_list(scheduledsessions)
    wg_list = get_wg_list(wg_name_list)
    ads = find_ads_for_meeting(meeting)
    for ad in ads:
        # set the default to avoid needing extra arguments in templates
        # django 1.3+
        ad.default_hostscheme = site_base_url

    time_slices,date_slices = build_all_agenda_slices(scheduledsessions, True)

    return HttpResponse(render_to_string("meeting/landscape_edit.html",
                                         {"schedule":schedule,
                                          "saveas": saveas,
                                          "saveasurl": saveasurl,
                                          "meeting_base_url": meeting_base_url,
                                          "site_base_url": site_base_url,
                                          "rooms":rooms,
                                          "time_slices":time_slices,
                                          "date_slices":date_slices,
                                          "modified": modified,
                                          "meeting":meeting,
                                          "area_list": area_list,
                                          "area_directors" : ads,
                                          "wg_list": wg_list ,
                                          "scheduledsessions": scheduledsessions,
                                          "show_inline": set(["txt","htm","html"]) },
                                         RequestContext(request)), mimetype="text/html")

##############################################################################
#  show the properties associated with an agenda (visible, public)
#    this page uses ajax PUT requests to the API
#
AgendaPropertiesForm = modelform_factory(Schedule, fields=('name','visible', 'public'))

@group_required('Area Director','Secretariat')
@decorator_from_middleware(GZipMiddleware)
def edit_agenda_properties(request, num=None, name=None):

    meeting = get_meeting(num)
    schedule = get_schedule(meeting, name)
    form     = AgendaPropertiesForm(instance=schedule)

    return HttpResponse(render_to_string("meeting/properties_edit.html",
                                         {"schedule":schedule,
                                          "form":form,
                                          "meeting":meeting},
                                         RequestContext(request)), mimetype="text/html")

##############################################################################
# show list of agendas.
#

@group_required('Area Director','Secretariat')
@decorator_from_middleware(GZipMiddleware)
def edit_agendas(request, num=None, order=None):

    #if request.method == 'POST':
    #    return agenda_create(request, num, name)

    meeting = get_meeting(num)
    user = request.user

    schedules = meeting.schedule_set
    if not has_role(user, 'Secretariat'):
        schedules = schedules.filter(visible = True) | schedules.filter(owner = user.get_profile())

    schedules = schedules.order_by('owner', 'name')

    return HttpResponse(render_to_string("meeting/agenda_list.html",
                                         {"meeting":   meeting,
                                          "schedules": schedules.all()
                                          },
                                         RequestContext(request)),
                        mimetype="text/html")

def agenda(request, num=None, name=None, base=None, ext=None):
    base = base if base else 'agenda'
    ext = ext if ext else '.html'
    if 'iPhone' in get_user_agent(request) and ext == ".html":
        base = 'm_agenda'
    mimetype = {".html":"text/html", ".txt": "text/plain", ".ics":"text/calendar", ".csv":"text/csv"}
    meeting = get_meeting(num)
    schedule = get_schedule(meeting, name)
    updated = Switches().from_object(meeting).updated()
    return HttpResponse(render_to_string("meeting/"+base+ext,
        {"schedule":schedule, "updated": updated}, RequestContext(request)), mimetype=mimetype[ext])

def read_agenda_file(num, doc):
    # XXXX FIXME: the path fragment in the code below should be moved to
    # settings.py.  The *_PATH settings should be generalized to format()
    # style python format, something like this:
    #  DOC_PATH_FORMAT = { "agenda": "/foo/bar/agenda-{meeting.number}/agenda-{meeting-number}-{doc.group}*", }
    path = os.path.join(settings.AGENDA_PATH, "%s/agenda/%s" % (num, doc.external_url))
    if os.path.exists(path):
        with open(path) as f:
            return f.read()
    else:
        return None

def session_agenda(request, num, session):
    d = Document.objects.filter(type="agenda", session__meeting__number=num)
    if session == "plenaryt":
        d = d.filter(session__name__icontains="technical", session__slots__type="plenary")
    elif session == "plenaryw":
        d = d.filter(session__name__icontains="admin", session__slots__type="plenary")
    else:
        d = d.filter(session__group__acronym=session)

    if d:
        agenda = d[0]
        content = read_agenda_file(num, agenda) or "Could not read agenda file"
        _, ext = os.path.splitext(agenda.external_url)
        ext = ext.lstrip(".").lower()

        if ext == "txt":
            return HttpResponse(content, mimetype="text/plain")
        elif ext == "pdf":
            return HttpResponse(content, mimetype="application/pdf")
        else:
            return HttpResponse(content)

    raise Http404("No agenda for the %s session of IETF %s is available" % (session, num))

def convert_to_pdf(doc_name):
    inpath = os.path.join(settings.IDSUBMIT_REPOSITORY_PATH, doc_name + ".txt")
    outpath = os.path.join(settings.INTERNET_DRAFT_PDF_PATH, doc_name + ".pdf")

    try:
        infile = open(inpath, "r")
    except IOError:
        return

    t,tempname = mkstemp()
    tempfile = open(tempname, "w")

    pageend = 0;
    newpage = 0;
    formfeed = 0;
    for line in infile:
        line = re.sub("\r","",line)
        line = re.sub("[ \t]+$","",line)
        if re.search("\[?[Pp]age [0-9ivx]+\]?[ \t]*$",line):
            pageend=1
            tempfile.write(line)
            continue
        if re.search("^[ \t]*\f",line):
            formfeed=1
            tempfile.write(line)
            continue
        if re.search("^ *INTERNET.DRAFT.+[0-9]+ *$",line) or re.search("^ *Internet.Draft.+[0-9]+ *$",line) or re.search("^draft-[-a-z0-9_.]+.*[0-9][0-9][0-9][0-9]$",line) or re.search("^RFC.+[0-9]+$",line):
            newpage=1
        if re.search("^[ \t]*$",line) and pageend and not newpage:
            continue
        if pageend and newpage and not formfeed:
            tempfile.write("\f")
        pageend=0
        formfeed=0
        newpage=0
        tempfile.write(line)

    infile.close()
    tempfile.close()
    t,psname = mkstemp()
    pipe("enscript --margins 76::76: -B -q -p "+psname + " " +tempname)
    os.unlink(tempname)
    pipe("ps2pdf "+psname+" "+outpath)
    os.unlink(psname)

def session_draft_list(num, session):
    try:
        agenda = Document.objects.filter(type="agenda",
                                         session__meeting__number=num,
                                         session__group__acronym=session,
                                         states=State.objects.get(type="agenda", slug="active")).distinct().get()
    except Document.DoesNotExist:
        raise Http404

    drafts = set()
    content = read_agenda_file(num, agenda)
    if content:
        drafts.update(re.findall('(draft-[-a-z0-9]*)', content))

    result = []
    for draft in drafts:
        try:
            if re.search('-[0-9]{2}$', draft):
                doc_name = draft
            else:
                doc = Document.objects.get(name=draft)
                doc_name = draft + "-" + doc.rev

            if doc_name not in result:
                result.append(doc_name)
        except Document.DoesNotExist:
            pass

    return sorted(result)

def session_draft_tarfile(request, num, session):
    drafts = session_draft_list(num, session);

    response = HttpResponse(mimetype='application/octet-stream')
    response['Content-Disposition'] = 'attachment; filename=%s-drafts.tgz'%(session)
    tarstream = tarfile.open('','w:gz',response)
    mfh, mfn = mkstemp()
    manifest = open(mfn, "w")

    for doc_name in drafts:
        pdf_path = os.path.join(settings.INTERNET_DRAFT_PDF_PATH, doc_name + ".pdf")

        if (not os.path.exists(pdf_path)):
            convert_to_pdf(doc_name)

        if os.path.exists(pdf_path):
            try:
                tarstream.add(pdf_path, str(doc_name + ".pdf"))
                manifest.write("Included:  "+pdf_path+"\n")
            except Exception, e:
                manifest.write(("Failed (%s): "%e)+pdf_path+"\n")
        else:
            manifest.write("Not found: "+pdf_path+"\n")

    manifest.close()
    tarstream.add(mfn, "manifest.txt")
    tarstream.close()
    os.unlink(mfn)
    return response

def pdf_pages(file):
    try:
        infile = open(file, "r")
    except IOError:
        return 0
    for line in infile:
        m = re.match('\] /Count ([0-9]+)',line)
        if m:
            return int(m.group(1))
    return 0


def session_draft_pdf(request, num, session):
    drafts = session_draft_list(num, session);
    curr_page = 1
    pmh, pmn = mkstemp()
    pdfmarks = open(pmn, "w")
    pdf_list = ""

    for draft in drafts:
        pdf_path = os.path.join(settings.INTERNET_DRAFT_PDF_PATH, draft + ".pdf")
        if (not os.path.exists(pdf_path)):
            convert_to_pdf(draft)

        if (os.path.exists(pdf_path)):
            pages = pdf_pages(pdf_path)
            pdfmarks.write("[/Page "+str(curr_page)+" /View [/XYZ 0 792 1.0] /Title (" + draft + ") /OUT pdfmark\n")
            pdf_list = pdf_list + " " + pdf_path
            curr_page = curr_page + pages

    pdfmarks.close()
    pdfh, pdfn = mkstemp()
    pipe("gs -dBATCH -dNOPAUSE -q -sDEVICE=pdfwrite -sOutputFile=" + pdfn + " " + pdf_list + " " + pmn)

    pdf = open(pdfn,"r")
    pdf_contents = pdf.read()
    pdf.close()

    os.unlink(pmn)
    os.unlink(pdfn)
    return HttpResponse(pdf_contents, mimetype="application/pdf")

def week_view(request, num=None):
    meeting = get_meeting(num)
    timeslots = TimeSlot.objects.filter(meeting__id = meeting.id)

    template = "meeting/week-view.html"
    return render_to_response(template,
            {"timeslots":timeslots,"render_types":["Session","Other","Break","Plenary"]}, context_instance=RequestContext(request))

def ical_agenda(request, num=None, name=None, ext=None):
    meeting = get_meeting(num)
    schedule = get_schedule(meeting, name)
    updated = Switches().from_object(meeting).updated()

    q = request.META.get('QUERY_STRING','') or ""
    filter = set(urllib.unquote(q).lower().split(','))
    include = [ i for i in filter if not (i.startswith('-') or i.startswith('~')) ]
    include_types = set(["plenary","other"])
    exclude = []

    # Process the special flags.
    #   "-wgname" will remove a working group from the output.
    #   "~Type" will add that type to the output.
    #   "-~Type" will remove that type from the output
    # Current types are:
    #   Session, Other (default on), Break, Plenary (default on)
    # Non-Working Group "wg names" include:
    #   edu, ietf, tools, iesg, iab

    for item in filter:
        if item:
            if item[0] == '-' and item[1] == '~':
                include_types -= set([item[2:]])
            elif item[0] == '-':
                exclude.append(item[1:])
            elif item[0] == '~':
                include_types |= set([item[1:]])

    assignments = schedule.assignments.filter(
        Q(timeslot__type__slug__in = include_types) |
        Q(session__group__acronym__in = include) |
        Q(session__group__parent__acronym__in = include)
        ).exclude(session__group__acronym__in = exclude).distinct()
        #.exclude(Q(session__group__isnull = False),
        #Q(session__group__acronym__in = exclude) |
        #Q(session__group__parent__acronym__in = exclude))

    return HttpResponse(render_to_string("meeting/agenda.ics",
        {"schedule":schedule, "assignments":assignments, "updated":updated},
        RequestContext(request)), mimetype="text/calendar")

def meeting_requests(request, num=None) :
    meeting = get_meeting(num)
    sessions = Session.objects.filter(meeting__number=meeting.number,group__parent__isnull = False).exclude(requested_by=0).order_by("group__parent__acronym","status__slug","group__acronym")

    groups_not_meeting = Group.objects.filter(state='Active',type__in=['WG','RG','BOF']).exclude(acronym__in = [session.group.acronym for session in sessions]).order_by("parent__acronym","acronym")

    return render_to_response("meeting/requests.html",
        {"meeting": meeting, "sessions":sessions,
         "groups_not_meeting": groups_not_meeting},
        context_instance=RequestContext(request))

