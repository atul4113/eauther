# -*- coding: utf-8 -*-
from libraries.wiki.util import make_url, has_access_to_wiki
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from libraries.utility.noseplugins import FormattedOutputTestCase
from nose.plugins.attrib import attr

class UtilTest(FormattedOutputTestCase):
    @attr('unit')
    def test_make_url_with_odd_chars(self):
        title = "coś tam coś tam i jeszcze dużo"
        url = make_url(title)
        expected = "cos-tam-cos-tam-i-jeszcze-duzo"
        self.assertEqual(url, expected)

    @attr('unit')
    def test_make_url_with_typical_char(self):
        title = "make my name"
        url = make_url(title)
        expected = "make-my-name"
        self.assertEqual(url, expected)

    @attr('unit')
    def test_make_url_whitespaces(self):
        title = "                  make my name                d\tsa"
        url = make_url(title)
        expected = "make-my-name-d-sa"
        self.assertEqual(url, expected)

    @attr('unit')
    def test_make_url_reserved_chars(self):
        title = "*&!@#$%^&!@#$%^&*()_+adsa"
        url = make_url(title)
        expected = "_adsa"
        self.assertEqual(url, expected)

    @attr('unit')
    def test_make_url_only_reserved_chars(self):
        title = "*&!@#$%^&!@#$%^&*()+"
        self.assertRaises(ValidationError, make_url, title)

    @attr('unit')
    def test_make_url_empty_title(self):
        title = ""
        self.assertRaises(ValidationError, make_url, title)

class AccessTest(FormattedOutputTestCase):
    fixtures = ['user.json']

    def test_check_access_to_wiki(self):
        user = User.objects.get(pk=6)
        self.assertTrue(has_access_to_wiki(user))

        user.is_superuser = False
        user.is_staff = False
        user.save()
        self.assertFalse(has_access_to_wiki(user))

        user.is_staff = True
        user.is_superuser = False
        user.save()
        self.assertTrue(has_access_to_wiki(user))

        user.is_staff = False
        user.is_superuser = True
        user.save()
        self.assertTrue(has_access_to_wiki(user))