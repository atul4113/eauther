from django.test.client import Client
from src.libraries.utility.noseplugins import FormattedOutputTestCase

class EmbedViewsTests(FormattedOutputTestCase):
    fixtures = ['embed.json']

    def setUp(self):
        self.client = Client()
        self.client.login(username='admin', password='test')

    def tearDown(self):
        self.client.logout()

    def test_admin_access_returns_true(self):
        self.client.login(username='admin', password='test')
        response = self.client.get('/embed/42')
        self.assertEqual(response.status_code, 200)
        
    def test_user_access_without_view_permission_return_false(self):
        self.client.login(username='test_bez_view', password='test')
        response = self.client.get('/embed/42')
        self.assertEqual(response.status_code, 404)

    def test_user_access_with_view_permission_return_true(self):
        self.client.login(username='test_z_view', password='test')
        response = self.client.get('/embed/42')
        self.assertEqual(response.status_code, 200)
    
    def test_owner_access_return_true(self):
        self.client.login(username='test_owner', password='test')
        response = self.client.get('/embed/42')
        self.assertEqual(response.status_code, 200)
        
    def test_user_without_permission_public_access_return_true(self):
        self.client.login(username='test_bez_view', password='test')
        response = self.client.get('/embed/246')
        self.assertEqual(response.status_code, 200)
        
    def test_user_with_permission_public_access_return_true(self):
        self.client.login(username='test_z_view', password='test')
        response = self.client.get('/embed/246')
        self.assertEqual(response.status_code, 200)
        
    def test_admin_public_access_return_true(self):
        self.client.login(username='admin', password='test')
        response = self.client.get('/embed/246')
        self.assertEqual(response.status_code, 200)

