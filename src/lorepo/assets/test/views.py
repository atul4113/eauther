from django.test.client import Client
from src.libraries.utility.noseplugins import FormattedOutputTestCase

class ViewsTests(FormattedOutputTestCase):
    fixtures = ['assets.json']

    def setUp(self):
        self.client = Client()
        self.client.login(username='test', password='test')

    def tearDown(self):
        self.client.logout()

    def test_browse_assets(self):
        response = self.client.get('/assets/107')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['assets']), 2)

        response = self.client.post('/assets/107', {'type' : 'image/jpeg'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['assets']), 2)

        response = self.client.post('/assets/107', {'type' : 'audio/wav'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['assets']), 0)

        response = self.client.post('/assets/107', {'type' : ''})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['assets']), 2)