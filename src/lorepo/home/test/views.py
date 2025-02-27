from django.test.client import Client
from src.libraries.utility.noseplugins import FormattedOutputTestCase

class ViewsTests(FormattedOutputTestCase):
    fixtures = ['home.json']

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        self.client.logout()

    def test_index(self):
        response= self.client.get('/')
        self.assertEqual(response.status_code, 200)