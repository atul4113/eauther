from django.test.client import Client
from libraries.utility.noseplugins import FormattedOutputTestCase

class ViewsTest(FormattedOutputTestCase):
    fixtures = ['lorepo.json']

    def setUp(self):
        self.client = Client()
        self.client.login(username='admin', password='admin')

    def tearDown(self):
        self.client.logout()

    def test_index_without_space_id(self):
        response = self.client.get('/spaces/')
        self.assertIsNone(response.context['space_id'])
        self.assertEqual(len(response.context['spaces']), 3)

    def test_index_with_space_id(self):
        response = self.client.get('/spaces/770')
        self.assertIsNotNone(response.context['space_id'])
        self.assertEqual(len(response.context['spaces']), 0)