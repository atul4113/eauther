from libraries.utility.noseplugins import QueueTestCase
from django.test.client import Client
from lorepo.mycontent.models import Content, CurrentlyEditing
from xml.dom import minidom
from django.contrib.auth.models import User

class AddTitleToXml(QueueTestCase):
    fixtures = ['add_title_to_xml.json']

    def setUp(self):
        super(AddTitleToXml, self).setUp()
        self.client = Client()
        self.client.login(username='kgebert', password='kgebert1')

    def tearDown(self):
        super(AddTitleToXml, self).tearDown()
        self.client.logout()
        
    def test_create_new_presentation(self):
        response = self.client.post('/mycontent/addcontent/1869', { 'title' : 'mAuthor', 'next' : '/', "score_type" : "last"})
        new_presentation = Content.objects.latest('created_date')
        doc = minidom.parseString(new_presentation.file.contents)
        ics = doc.getElementsByTagName('interactiveContent')
        ic = ics[0]
        
        self.assertEqual(302, response.status_code)
        self.assertEqual(1, len(ics))
        self.assertEqual('mAuthor', ic.getAttribute('name'))
        
    def test_edit_metadata(self):
        response = self.client.post('/corporate/2025/metadata', { 'title' : 'mAuthor', 'space_id' : 1869, 'next' : '/', "score_type" : "last" })
        edited_presentation = Content.objects.get(pk=2025)
        doc = minidom.parseString(edited_presentation.file.contents)
        ics = doc.getElementsByTagName('interactiveContent')
        ic = ics[0]
        
        self.assertEqual(302, response.status_code)
        self.assertEqual(1, len(ics))
        self.assertEqual('mAuthor', ic.getAttribute('name'))
        
    def test_edit_metadata_when_some1_is_currently_editing(self):
        edited_presentation = Content.objects.get(pk=2064)
        user = User.objects.get(pk=1)
        currently_editing = CurrentlyEditing(content=edited_presentation, user=user)
        currently_editing.save()
        response = self.client.post('/corporate/2064/metadata', { 'title' : 'mAuthor', 'space_id' : 1869, 'next' : '/' , "score_type" : "last"})
        doc = minidom.parseString(edited_presentation.file.contents)
        ics = doc.getElementsByTagName('interactiveContent')
        ic = ics[0]
        
        self.assertEqual(302, response.status_code)
        self.assertEqual(1, len(ics))
        self.assertEqual('Localized for test', ic.getAttribute('name'), 'title in xml should NOT change')