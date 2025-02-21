# -*- coding: utf-8 -*-
from django.test.client import Client
from lorepo.mycontent.models import Content
from lorepo.mycontent.templatetags.content import cut_after
from libraries.utility.noseplugins import FormattedOutputTestCase
from libraries.utility.test_assertions import status_code_for, the
import xml.etree.ElementTree as ET

class TemplatesTests(FormattedOutputTestCase):
    fixtures = ['url.json']

    def setUp(self):
        self.client = Client()
        self.client.login(username='kgebert', password='kgebert1')

    def tearDown(self):
        self.client.logout()

    def test_copy_option(self):
        '''Checks if copy option has correct redirect url attached.
        '''
        response = self.client.get('/mycontent/398')
        status_code_for(response).should_be(200)
        self.assertContains(response, '<option value="/mycontent/copy/455">')

        response = self.client.get('/mycontent')
        status_code_for(response).should_be(200)
        self.assertContains(response, '<option value="/mycontent/copy/451">')

    def test_show_history_option(self):
        '''Checks if show history option is present
        '''
        response = self.client.get('/mycontent/')
        self.assertContains(response, '<option data-url="/mycontent/451/history">')

    def test_cut_after_filter(self):
        title = "Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat."
        cut = cut_after(title, 40)
        self.assertEqual(cut, "Lorem ipsum dolor sit amet, consectetuer...")

        title = 'Lorem_ipsum_dolor_sit_amet,_consectetuer_____________ASDASD______________ADSASDASD_____________DASDASLA'
        cut = cut_after(title, 40)
        self.assertEqual(cut, "Lorem_ipsum_dolor_sit_amet,_consectetuer...")

class UpdateTemplateTests(FormattedOutputTestCase):
    fixtures = ['update_templates.json']

    def setUp(self):
        self.client = Client()
        self.client.login(username='admin', password='admin')

    def tearDown(self):
        self.client.logout()

    def test_update_template(self):
        content = Content.objects.get(pk=28)
        original_page = ET.fromstring(content.file.contents)
        original_style = original_page.findall('style')[0].text
        for entry in original_page.findall('entry'):
            if entry.get('key') == 'theme.href':
                original_theme_href = entry.get('value')
        response = self.client.get("/mycontent/updatetemplate/28?next=/corporate/list/18")
        status_code_for(response).should_be(302)

        content = Content.objects.get(pk=28)
        changed_page = ET.fromstring(content.file.contents)
        changed_style = changed_page.findall('style')[0].text
        the(changed_style).does_not_equal(original_style)
        the(changed_style).equals('.ic_page { font-size: 12px }')
        for entry in changed_page.findall('entry'):
            if entry.get('key') == 'theme.href':
                new_theme_href = entry.get('value')
                the(new_theme_href).does_not_equal(original_theme_href)
        
        addon_descriptors = changed_page.findall('addons')[0].findall('addon-descriptor')
        the(len(addon_descriptors)).equals(2)
        addon_descriptor = addon_descriptors[1]
        the(addon_descriptor.attrib['addonId']).equals('YouTube_Addon')
        the(addon_descriptor.attrib['href']).equals('http://www.mauthor.com/media/iceditor/addons/YouTube_Addon.xml')