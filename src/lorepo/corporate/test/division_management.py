from django.test.client import Client
from libraries.utility.noseplugins import FormattedOutputTestCase
from lorepo.spaces.models import Space

class AccessRightsTest(FormattedOutputTestCase):
    fixtures = ['corporate_spaces.json']

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        self.client.logout()

    def test_list_divisions_company_admin(self):
        self.client.login(username='test2', password='test')
        response = self.client.get('/corporate/divisions')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['divisions']), 3)

    def test_list_divisions_no_access(self):
        self.client.login(username='test3', password='test')
        response = self.client.get('/corporate/divisions')
        self.assertEqual(response.status_code, 403)

class ProjectManagement(FormattedOutputTestCase):
    fixtures = ['projects_management.json']

    def setUp(self):
        self.client = Client()
        self.client.login(username='test', password='test')

    def tearDown(self):
        self.client.logout()

    def test_remove_project(self):
        self.client.get('/corporate/18/delete_space')
        project = Space.objects.get(pk = 18) # 19 is a publication in project 18
        
        self.assertEqual(project.is_deleted, True)
        
        self.assertEqual(project.parent, None)
        
        self.assertEqual(project.top_level, None)
        
        self.assertEqual(project.spaceaccess_set.count(), 0)
        