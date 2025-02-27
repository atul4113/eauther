from django.test.client import Client
import json
from minimock import Mock
import urllib.request, urllib.error, urllib.parse
from src.libraries.utility.noseplugins import FormattedOutputTestCase

EXPECTED = '''{
	"version": "1",
	"addons": [
		{
			"id" : "AddonAli",
			"name" : "_Addon_Ali_",
			"icon_url": "http://testserver/media/content/default_small_addon.png",
			"descriptor_url": "/proxy/get?url=http://testserver/mycontent/AddonAli/getaddon",
			"category" : "Private"
		},
		{
			"id" : "CompanyAddon",
			"name" : "_Company_addon_",
			"icon_url": "http://testserver/media/content/default_small_addon.png",
			"descriptor_url": "/proxy/get?url=http://testserver/mycontent/CompanyAddon/getaddon",
            "category" : "Private"
		},
        {
            "id" : "PublicznyAddonAli",
            "name" : "_Publiczny_Addon_Ali_",
            "icon_url": "http://testserver/media/content/default_small_addon.png",
            "descriptor_url": "/proxy/get?url=http://testserver/mycontent/PublicznyAddonAli/getaddon",
            "category" : "Private"
        }
	]
}
'''

class AddonsTemplateTests(FormattedOutputTestCase):
    fixtures = ['addons.json']

    def setUp(self):
        self.client = Client()
        self.maxDiff = None
        urllib.request.urlopen = Mock('Mocked_urllib2_urlopen')
        mocked_urllib = Mock('Mocked_urllib2_urlopen')
        mocked_urllib.read.mock_returns = '''{"version": "1", "addons": []}'''
        urllib.request.urlopen.mock_returns = mocked_urllib

    def tearDown(self):
        self.client.logout()

    def _addons(self):
        '''Checks if output JSON structure is OK.
        Test disabled as for now we only read addons from src.lorepo.com
    	'''
        self.client.login(username='ala', password='ala')
        response = self.client.get('/editor/api/addons')
        expected = json.loads(EXPECTED)
        resp = json.loads(response.content)
        self.assertEqual(resp, expected)
