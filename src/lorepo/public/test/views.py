from django.test.client import Client
from src.libraries.utility.noseplugins import FormattedOutputTestCase
from src.lorepo.mycontent.models import Content

class ViewsTest(FormattedOutputTestCase):
    fixtures = ['public.json']

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        self.client.logout()

    def test_view_positive(self):
        '''
        Fixture public.json contain inconsistent public lesson data, so they're fixed by hand in tests
        ''' 
        content = Content.objects.get(pk=319)
        content.is_public = True
        content.save()
        
        self.client.login(username="ala", password="ala")
        response = self.client.get('/public/view/319', follow = True)
        self.assertEqual(response.status_code, 200) # redirect to embed
        self.assertIsNotNone(response.context['content'])

    def test_view_as_superuser(self):
        self.client.login(username='admin', password='admin')
        response = self.client.get('/public/view/4', follow = True)
        self.assertEqual(response.status_code, 200, 'Superuser should be allowed to view non public content')
        self.assertIsNotNone(response.context['content'])

    def test_view_as_regular_user(self):
        # Content that is not public
        self.client.login(username='ala', password='ala')
        response = self.client.get('/public/view/4', follow = True)
        self.assertEqual(response.status_code, 404, 'Non public content should not be displayed')

    def test_view_negative(self):
        # No content id
        response = self.client.get('/public/view')
        self.assertEqual(response.status_code, 404)

        response = self.client.get('/public/view/')
        self.assertEqual(response.status_code, 404)

        # Non existing content
        response = self.client.get('/public/view/1234567890', follow = True)
        self.assertEqual(response.status_code, 404, '404 should be returned for non existing content')

        # Content that is not public
        response = self.client.get('/public/view/4', follow = True)
        self.assertEqual(response.status_code, 404, 'Non public content should not be displayed')

