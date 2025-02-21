from libraries.utility.noseplugins import FormattedOutputTestCase
from django.test.client import Client
from lorepo.mycontent.models import Content
from mauthor.exchange_narration.model import ExportNarration
from libraries.utility.helpers import get_object_or_none
from lorepo.filestorage.models import FileStorage
from xml.dom import minidom
from django.contrib.auth.models import User

class ExportNarrationTests(FormattedOutputTestCase):
    fixtures = ['exchange_narration/export_narration.json'] # localization/fixtures

    def setUp(self):
        self.client = Client()
        self.content = Content.objects.get(pk = 35)
        
    def test_get_pages(self):
        export = ExportNarration(self.content)
        pages = export.get_pages()
        
        self.assertEqual(6, len(pages))
        self.assertEqual('Page 1', pages[0].name)
        self.assertEqual('328', pages[0].href)
        self.assertEqual(1, pages[0].index)
        
    def test_set_narrations(self):
        export = ExportNarration(self.content)
        export.set_pages()

        export.set_narrations()

        self.assertEqual(1, len(export.pages[0].narrations))
        self.assertEqual('Hi, this is narration test. I would like to ask you how do you feel.', export.pages[0].narrations[0].value)
        
    def test_get_narration_elements(self):
        export = ExportNarration(self.content)
        export.set_pages()
        
        page_file = get_object_or_none(FileStorage, pk = export.pages[0].href)
        page_doc = minidom.parseString(page_file.contents)
        narration_elements = export.get_narration_elements(page_doc)
        
        self.assertEqual(1, len(narration_elements))
        
    def test_create_csv_will_return_file_storage(self):
        export = ExportNarration(self.content)
        export.set_pages()
        user = User.objects.get(username = 'kgebert')
        
        csv_file = export.create_csv(user)
        
        self.assertTrue(isinstance(csv_file, FileStorage))