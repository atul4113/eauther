from django.test.client import RequestFactory
from django.contrib.auth.models import User, AnonymousUser
from lorepo.corporate.middleware import CorporateMiddleware
from libraries.utility.noseplugins import FormattedOutputTestCase
import lorepo.corporate.middleware as middleware
import re
from nose.plugins.attrib import attr

class CorporateMiddlewareTest(FormattedOutputTestCase):
    fixtures = ['corporate.json']

    def setUp(self):
        self.factory = RequestFactory()

    def tearDown(self):
        pass

    def test_process_request_company_admin(self):
        request = self.factory.get('/')
        request.user = User.objects.get(username='test')
        middleware = CorporateMiddleware()
        middleware.process_request(request)

        self.assertIsNotNone(request.user.company)
        self.assertEqual(request.user.company.title, 'Solwit')
        self.assertIsNotNone(request.user.public_category)
        self.assertEqual(request.user.public_category.title, 'Solwit Public')
        self.assertIsNotNone(request.user.divisions)
        division_titles = [d.title for d in list(request.user.divisions.values())]
        self.assertIn('Solwit IT', division_titles)
        self.assertIn('Solwit HR', division_titles)
        self.assertIn('Solwit Board', division_titles)

    def test_process_request_user_assigned_to_division(self):
        request = self.factory.get('/')
        request.user = User.objects.get(username='test2')
        middleware = CorporateMiddleware()
        middleware.process_request(request)

        self.assertIsNotNone(request.user.company)
        self.assertEqual(request.user.company.title, 'Solwit')
        self.assertIsNotNone(request.user.public_category)
        self.assertEqual(request.user.public_category.title, 'Solwit Public')
        self.assertIsNotNone(request.user.divisions)
        division_titles = [d.title for d in list(request.user.divisions.values())]
        self.assertIn('Solwit Board', division_titles)
        self.assertNotIn('Solwit IT', division_titles)
        self.assertNotIn('Solwit HR', division_titles)

    def test_process_request_user_assigned_to_project(self):
        request = self.factory.get('/')
        request.user = User.objects.get(username='test3')
        middleware = CorporateMiddleware()
        middleware.process_request(request)

        self.assertIsNotNone(request.user.company)
        self.assertEqual(request.user.company.title, 'Solwit')
        self.assertIsNotNone(request.user.public_category)
        self.assertEqual(request.user.public_category.title, 'Solwit Public')
        self.assertIsNotNone(request.user.divisions)
        division_titles = [d.title for d in list(request.user.divisions.values())]
        self.assertIn('Solwit IT', division_titles)
        self.assertNotIn('Solwit IT Project', division_titles)

    def test_process_request_anonymous_user(self):
        request = self.factory.get('/')
        request.user = AnonymousUser()
        middleware = CorporateMiddleware()
        middleware.process_request(request)

class SkippedURLSTest(FormattedOutputTestCase):
    @attr('unit')
    def test_skip_filestorage(self):
        self.assertIsNotNone(middleware.SKIPPED_URLS.match('/file/1234'))
        self.assertIsNotNone(middleware.SKIPPED_URLS.match('/file/serve/1234'))
        self.assertIsNone(middleware.SKIPPED_URLS.match('test/file/serve/1234'))

    @attr('unit')
    def test_skip_uploaddir(self):
        self.assertIsNotNone(middleware.SKIPPED_URLS.match('/editor/api/blobUploadDir'))
        self.assertIsNone(middleware.SKIPPED_URLS.match('/editor/api/templates'))

    @attr('unit')
    def test_skip_proxy(self):
        self.assertIsNotNone(middleware.SKIPPED_URLS.match('/proxy/get'))