from django.test.client import Client
import json
from libraries.utility.noseplugins import FormattedOutputTestCase

class TemplatesTests(FormattedOutputTestCase):
    fixtures = ['templates.json']

    def setUp(self):
        self.client = Client()
        self.maxDiff = None
        self.client.login(username='kgebert', password='kgebert1')

    def tearDown(self):
        self.client.logout()

    def test_get_corporate_templates(self):
        response = self.client.get('/editor/api/templates')
        
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.context['templates']), 4)
        self.assertEqual('Public', list(response.context['templates'])[0].category)
        self.assertEqual('Public', list(response.context['templates'])[1].category)
        self.assertEqual('Private', list(response.context['templates'])[2].category)
        self.assertEqual('Private', list(response.context['templates'])[3].category)

    def test_templates_json(self):
        response = self.client.get('/editor/api/templates')
        expected = json.loads(EXPECTED_JSON)
        resp = json.loads(response.content)
        self.assertEqual(resp, expected)

EXPECTED_JSON = '''{
        "version": "1",
        "items": [
        {
                "id" : "1439",
                "name" : "Gases: Handling and Laboratory Tests",
                "icon_url": "http://testserver/file/serve/1951021",
                "theme_url": "/file/1487",
                "category" : "Public"
        },
        {
                "id" : "1426",
                "name" : "Testing for Ions ",
                "icon_url": "http://testserver/file/serve/1987087",
                "theme_url": "/file/1425",
                "category" : "Public"
        },
        {
                "id" : "1443",
                "name" : "template test",
                "icon_url": "http://testserver/media/content/default_presentation.png",
                "theme_url": "/file/1442",
                "category" : "Private"
        },
        {
                "id" : "1448",
                "name" : "template test 2",
                "icon_url": "http://testserver/media/content/default_presentation.png",
                "theme_url": "/file/1447",
                "category" : "Private"
        }
    ]
}'''
