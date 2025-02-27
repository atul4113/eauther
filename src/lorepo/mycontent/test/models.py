from django.test.client import Client
from src.libraries.utility.noseplugins import QueueTestCase

class ContentTests(QueueTestCase):
    fixtures = ['models.json']

    def setUp(self):
        super(ContentTests, self).setUp()
        self.client = Client()
        self.client.login(username='test', password='test')

    def tearDown(self):
        super(ContentTests, self).tearDown()
        self.client.logout()

    def test_name_field_uniqueness(self):
        '''Content's name field should be unique if not blank.
        '''
        response = self.client.post('/mycontent/addon', { "title" : "Present Perfect", "tags" : "english,perfect", "description" : "present perfect", "name" : "present_perfect1"})
        self.assertEqual(response.status_code, 302)
        response = self.client.post('/mycontent/addon', { "title" : "Present Perfect", "tags" : "english,perfect", "description" : "present perfect", "name" : "present_perfect2"})
        self.assertEqual(response.status_code, 302)

        response = self.client.post('/mycontent/addon', { "title" : "Present Perfect", "name" : "present_perfect"})
        self.assertEqual(response.status_code, 302)
        response = self.client.post('/mycontent/addon', { "title" : "Present Perfect", "name" : "present_perfect"})
        self.assertEqual(response.status_code, 200, "This should not validate - name already in use")
