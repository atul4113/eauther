from django.test.client import Client
from libraries.utility.noseplugins import FormattedOutputTestCase
from lorepo.mycontent.models import Content
from libraries.utility.test_assertions import the, status_code_for

class ExtractPagesTests(FormattedOutputTestCase):
    fixtures = ['extract_pages.json']

    def setUp(self):
        super(ExtractPagesTests, self).setUp()
        self.client = Client()
        self.client.login(username='test', password='test')

    def tearDown(self):
        super(ExtractPagesTests, self).tearDown()
        self.client.logout()

    def test_extract_pages(self):
        # GIVEN 
        the(Content.objects.count()).equals(1)

        # WHEN
        response = self.client.post('/mycontent/extract/4925812092436480/6192449487634432?next=/test', {'pages[0]' : 'on', 'pages[2]' : 'on'})
        status_code_for(response).should_be(302)
        self.assertEqual(response['location'], "http://testserver/test")

        # THEN
        the(Content.objects.count()).equals(2)
        the(Content.objects.latest('created_date').get_pages()).length_is(2)