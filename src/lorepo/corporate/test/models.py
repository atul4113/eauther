from src.libraries.utility.noseplugins import FormattedOutputTestCase
from django.test.client import RequestFactory, Client
from src.lorepo.mycontent.models import Content
from src.lorepo.spaces.models import Space


class PublicContentCheckTest(FormattedOutputTestCase):
    fixtures = ['publish.json']

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.client.login(username='owner1', password='owner1')

    def tearDown(self):
        self.client.logout()
        
    def test_should_be_public(self):
        content = Content.objects.get(pk=375)
        content.is_public = True
        content.public_version_id = 374
        
        self.assertTrue(content.is_content_public())
        
    def test_should_be_not_public(self):
        content = Content.objects.get(pk=375)
        content.is_public = False
        content.public_version_id = None
        
        self.assertFalse(content.is_content_public())
        
    def test_should_be_not_public_regression_check(self):
        content = Content.objects.get(pk=375)
        content.is_public = True
        content.public_version_id = None
        
        self.assertFalse(content.is_content_public())
        
        content.is_public = False
        content.public_version_id = 374
        
        self.assertFalse(content.is_content_public())

class SpaceLevelTests(FormattedOutputTestCase):
    fixtures = ['space_level.json']
    
    COMPANY_ID = 5770237022568448
    PROJECT_ID = 5488762045857792
    PUBLICATION_ID = 6614661952700416

    def test_space_is_company_true(self):
        space = Space.objects.get(pk = self.COMPANY_ID)

        self.assertTrue(space.is_company())

    def test_space_is_company_false(self):
        space = Space.objects.get(pk = self.PROJECT_ID)

        self.assertFalse(space.is_company())

    def test_space_is_project_true(self):
        space = Space.objects.get(pk = self.PROJECT_ID)

        self.assertTrue(space.is_project())

    def test_space_is_project_false(self):
        space = Space.objects.get(pk = self.PUBLICATION_ID)

        self.assertFalse(space.is_project())

    def test_space_is_publication_true(self):
        space = Space.objects.get(pk = self.PUBLICATION_ID)

        self.assertTrue(space.is_publication())

    def test_space_is_publication_false(self):
        space = Space.objects.get(pk = self.PROJECT_ID)

        self.assertFalse(space.is_publication())