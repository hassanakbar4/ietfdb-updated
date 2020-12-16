# Copyright The IETF Trust 2009-2020, All Rights Reserved
# -*- coding: utf-8 -*-
#
# Portion Copyright (C) 2009 Nokia Corporation and/or its subsidiary(-ies).
# All rights reserved. Contact: Pasi Eronen <pasi.eronen@nokia.com>
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
#
#  * Neither the name of the Nokia Corporation and/or its
#    subsidiary(-ies) nor the names of its contributors may be used
#    to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import os
import re
import email
import html5lib
import inspect
import sys

from urllib.parse import unquote

from unittest.util import strclass
from bs4 import BeautifulSoup

import django.test
from django.conf import settings
from django.utils.text import slugify

import debug                            # pyflakes:ignore

from ietf.utils.mail import get_payload_text

real_database_name = settings.DATABASES["default"]["NAME"]

def split_url(url):
    if "?" in url:
        url, args = url.split("?", 1)
        args = dict([ list(map(unquote,arg.split("=", 1))) for arg in args.split("&") if "=" in arg ])
    else:
        args = {}
    return url, args

def login_testing_unauthorized(test_case, username, url, password=None):
    r = test_case.client.get(url)
    test_case.assertIn(r.status_code, (302, 403))
    if r.status_code == 302:
        test_case.assertTrue("/accounts/login" in r['Location'])
    if not password:
        password = username + "+password"
    return test_case.client.login(username=username, password=password)

def unicontent(r):
    "Return a HttpResponse object's content as unicode"
    return r.content.decode(r.charset)

def textcontent(r):
    text = BeautifulSoup(r.content, 'lxml').get_text()
    text = re.sub(r'(\n\s+){2,}', '\n\n', text)
    return text

def reload_db_objects(*objects):
    """Rerequest the given arguments from the database so they're refreshed, to be used like

    foo, bar = reload_db_objects(foo, bar)"""

    t = tuple(o.__class__.objects.get(pk=o.pk) for o in objects)
    if len(objects) == 1:
        return t[0]
    else:
        return t

def assert_ical_response_is_valid(test_inst, response, expected_event_summaries=None,
                                  expected_event_uids=None, expected_event_count=None):
    """Validate an HTTP response containing iCal data

    Based on RFC2445, but not exhaustive by any means. Assumes a single iCalendar object. Checks that
    expected_event_summaries/_uids are found, but other events are allowed to be present. Specify the
    expected_event_count if you want to reject additional events. If any of these are None,
    the check for that property is skipped.
    """
    test_inst.assertEqual(response.get('Content-Type'), "text/calendar")

    # Validate iCalendar object
    test_inst.assertContains(response, 'BEGIN:VCALENDAR', count=1)
    test_inst.assertContains(response, 'END:VCALENDAR', count=1)
    test_inst.assertContains(response, 'PRODID:', count=1)
    test_inst.assertContains(response, 'VERSION', count=1)

    # Validate event objects
    if expected_event_summaries is not None:
        for summary in expected_event_summaries:
            test_inst.assertContains(response, 'SUMMARY:' + summary)

    if expected_event_uids is not None:
        for uid in expected_event_uids:
            test_inst.assertContains(response, 'UID:' + uid)

    if expected_event_count is not None:
        test_inst.assertContains(response, 'BEGIN:VEVENT', count=expected_event_count)
        test_inst.assertContains(response, 'END:VEVENT', count=expected_event_count)
        test_inst.assertContains(response, 'UID', count=expected_event_count)



class ReverseLazyTest(django.test.TestCase):
    def test_redirect_with_lazy_reverse(self):
        response = self.client.get('/ipr/update/')
        self.assertRedirects(response, "/ipr/", status_code=301)

class TestCase(django.test.TestCase):
    """
    Does basically the same as django.test.TestCase, but adds asserts for html5 validation.
    """

    parser = html5lib.HTMLParser(strict=True)

    def assertValidHTML(self, data):
        try:
            self.parser.parse(data)
        except Exception as e:
            raise self.failureException(str(e))

    def assertValidHTMLResponse(self, resp):
        self.assertHttpOK(resp)
        self.assertTrue(resp['Content-Type'].startswith('text/html'))
        self.assertValidHTML(resp.content)

    def assertSameEmail(self, a, b, msg=None):
        def normalize(x):
            if x:
                if not isinstance(x, list):
                    x = [ x ]
                x = email.utils.getaddresses(x)
                x.sort()
            return x
        return self.assertEqual(normalize(a), normalize(b), msg)

    def tempdir(self, label):
        slug = slugify(self.__class__.__name__.replace('.','-'))
        dirname = "tmp-{label}-{slug}-dir".format(**locals())
        if 'VIRTUAL_ENV' in os.environ:
            dirname = os.path.join(os.environ['VIRTUAL_ENV'], dirname)
        path = os.path.abspath(dirname)
        if not os.path.exists(path):
            os.mkdir(path)
        return path

    def assertNoPageErrors(self, response, error_css_selector=".has-error"):
        from pyquery import PyQuery
        from lxml import html
        self.maxDiff = None

        errors = [html.tostring(n).decode() for n in PyQuery(response.content)(error_css_selector)]
        if errors:
            explanation = "Got page with errors:\n----\n" + "----\n".join(errors)
            raise AssertionError(explanation)

    def assertNoFormPostErrors(self, response, error_css_selector=".has-error"):
        """Try to fish out form errors, if none found at least check the
        status code to be a redirect.

        Assumptions:
         - a POST is followed by a 302 redirect
         - form errors can be found with a simple CSS selector

        """

        if response.status_code == 200:
            self.assertNoPageErrors(response, error_css_selector)

        self.assertEqual(response.status_code, 302)
        
    def assertMailboxContains(self, mailbox, subject=None, text=None, count=None):
        """
        Asserts that the given mailbox contains *count* mails with the given
        *subject* and body *text* (if not None).  At least one of subject,
        text, and count must be different from None.  If count is None, the
        filtered mailbox must be non-empty.
        """
        if subject is None and text is None and count is None:
            raise self.failureException("No assertion made, both text and count is None")
        mlist = mailbox
        if subject:
            mlist = [ m for m in mlist if subject in m["Subject"] ]
        if text:
            assert isinstance(text, str)
            mlist = [ m for m in mlist if text in get_payload_text(m) ]
        if count and len(mlist) != count:
            sys.stderr.write("Wrong count in assertMailboxContains().  The complete mailbox contains %s emails:\n\n" % len(mailbox))
            for m in mailbox:
                sys.stderr.write(m.as_string())
                sys.stderr.write('\n\n')
        if count:
            self.assertEqual(len(mlist), count)
        else:
            self.assertGreater(len(mlist), 0)

    def assertResponseStatus(self, r, code, msg_prefix=None):
        if r.status_code != code:
            self.assertNoPageErrors(r)
            sys.stderr.write(textcontent(r))
            raise AssertionError("%s%s != %s" % ("%s: "%msg_prefix if msg_prefix else '', r.status_code, code))
            

    def __str__(self):
        return u"%s (%s.%s)" % (self._testMethodName, strclass(self.__class__),self._testMethodName)


    def debug_save_response(self, r):
        """
        This is intended as a debug help, to be inserted whenever one wants
        to save a page response in a test case; not for production.
        """
        stack = inspect.stack()         # stack[0] is the current frame
        caller = stack[1]
        fn = caller.function + '.html'
        with open(fn, 'bw') as f:
            f.write(r.content)
            sys.stderr.write(f'Wrote response to {fn}\n')
            