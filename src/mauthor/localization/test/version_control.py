from libraries.utility.noseplugins import FormattedOutputTestCase,\
    QueueTestCase
from lorepo.mycontent.models import Content
from django.test.client import Client
from lorepo.filestorage.models import FileStorage
from mauthor.localization.models import Xliff
from xml.dom import minidom

class VersionControlTests(FormattedOutputTestCase):
    fixtures = ['version_control.json']
    
    def setUp(self):
        super(VersionControlTests, self).setUp()
        self.client = Client()
        self.client.login(username='kgebert', password='kgebert1')
    
    def tearDown(self):
        super(VersionControlTests, self).tearDown()
    
    def test_opening_editor_puts_new_versions(self):
        content = Content.objects.get(pk=2414)
        response = self.client.get('/localization/editor/2414?next=/corporate/list/1259')
        versions = list(FileStorage.objects.filter(history_for=content))
        xml_versions = [v for v in versions if v.content_type == 'text/xml']
        xliff_versions = [v for v in versions if v.content_type == 'application/x-xliff+xml']
        
        self.assertEqual(4, len(versions))
        self.assertEqual(2, len(xml_versions))
        self.assertEqual(2, len(xliff_versions))
        self.assertEqual(200, response.status_code)
        
    def test_show_history_shows_only_xml(self):
        response = self.client.get('/mycontent/2414/history')
        
        self.assertEqual(1, len(response.context['versions']))
        self.assertEqual('text/xml', response.context['versions'][0].content_type)
   
class CheckVersionsAndResetTests(QueueTestCase):
    fixtures = ['check_versions.json']
    
    def setUp(self):
        super(CheckVersionsAndResetTests, self).setUp()
        self.client = Client()
        self.client.login(username='kgebert', password='kgebert1')
    
    def tearDown(self):
        super(CheckVersionsAndResetTests, self).tearDown()
    
    def test_check_versions_when_both_are_valid(self):
        response = self.client.get('/localization/check_versions/3992?next=/corporate/list/1259')
        
        self.assertEqual(200, response.status_code)
        self.assertEqual('test', response.context['original_title'])
        self.assertEqual(3992, response.context['localized_content'].id)
        
    def test_check_versions_when_localized_has_changed(self):
        response = self.client.get('/mycontent/3992/editor?next=/corporate/list/1259')
        content = Content.objects.get(pk=3992)
        self.assertEqual(200, response.status_code)
        self.assertEqual(2, content.file.version)
        response = self.client.get('/mycontent/3992/exit_editor')
        
        response = self.client.get('/localization/check_versions/3992?next=/corporate/list/1259')
        self.assertEqual('3992', response.context['content_id'])
        self.assertEqual('/corporate/list/1259', response.context['next_url'])
        
    def test_check_versions_when_original_has_changed(self):
        response = self.client.get('/mycontent/3649/editor?next=/corporate/list/1259')
        content = Content.objects.get(pk=3649)
        self.assertEqual(200, response.status_code)
        self.assertEqual(8, content.file.version)
        
        response = self.client.get('/localization/check_versions/3992?next=/corporate/list/1259')
        self.assertEqual(200, response.status_code)
        self.assertContains(response, 'Update')
        
    def test_reset_to_original(self):
        content = Content.objects.get(pk=3992)
        
        response = self.client.get('/mycontent/3649/editor?next=/corporate/list/1259')
        xliff_document = minidom.parseString(content.xliff_file.contents)
        xliff = Xliff(xliff_document)
        self.assertEqual(200, response.status_code)
        self.assertEqual(6, xliff.get_original_version())
        
        content = Content.objects.get(pk=3992)
        
        response = self.client.get('/localization/reset_xliff_to_original/3992?next=/corporate/list/1258')
        xliff_document = minidom.parseString(content.xliff_file.contents)
        xliff = Xliff(xliff_document)
        self.assertEqual(302, response.status_code)
        self.assertEqual(8, xliff.get_original_version())

    def test_reset_to_current(self):
        content = Content.objects.get(pk=3992)
        
        response = self.client.get('/mycontent/3992/editor?next=/corporate/list/1259')
        xliff_document = minidom.parseString(content.xliff_file.contents)
        xliff = Xliff(xliff_document)
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, xliff.get_localized_version())
        
        content = Content.objects.get(pk=3992)
        
        response = self.client.get('/localization/reset_xliff_to_current/3992?next=/corporate/list/1258')
        xliff_document = minidom.parseString(content.xliff_file.contents)
        xliff = Xliff(xliff_document)
        self.assertEqual(302, response.status_code)
        self.assertEqual(2, xliff.get_localized_version())
