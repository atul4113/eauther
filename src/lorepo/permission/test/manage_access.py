from libraries.utility.noseplugins import FormattedOutputTestCase
from django.test.client import Client
from lorepo.spaces.models import SpaceAccess, Space
from django.contrib.auth.models import User
from lorepo.permission.models import Role
import logging

class ManageAccessTests(FormattedOutputTestCase):
    fixtures = ['permission_manage_access.json']

    def setUp(self):
        self.client = Client()
        self.client.login(username = 'kgebert', password = 'kgebert1')

    def tearDown(self):
        self.client.logout()

    def test_manage_access_index_space_access_and_role_count(self):
        response = self.client.get('/permission')

        self.assertEqual(3, len(response.context['roles']))

    def test_remove_space_access(self):
        response = self.client.get('/permission/remove_access/14')

        self.assertEqual(0, SpaceAccess.objects.get(pk = 14).is_deleted)

    def test_edit_space_access(self):
        response = self.client.post('/permission/edit_access/14', { 'roles' : ['1', '2', '3'] })

        self.assertEqual([1, 2, 3], SpaceAccess.objects.get(pk = 14).roles)

    def test_add_space_access(self):
        self.test3 = User.objects.create_user('test4', 'test4@test.pl', 'test')

        response = self.client.post('/permission/add_access', { 'user' : 'test4', 'space' : '12', 'roles' : ['1', '2', '3']})

        space_access_latest = SpaceAccess.objects.all().latest('created_date')
        self.assertEqual([1, 2, 3], space_access_latest.roles)

    def test_edit_role(self):
        response = self.client.post('/permission/edit_role/113', { 'permissions' : ['Browse Assets'] })

        self.assertEqual(1, len(Role.objects.get(pk = 113).permissions))

    def test_remove_role(self):
        self.client.post('/permission/add_role', { 'name' : 'test', 'permissions': ['Browse Assets'] })
        latest_role = Role.objects.all().latest('created_date')
        company = Space.objects.get(pk = 12)

        self.assertEqual(4, len(Role.objects.filter(company = company)))

        response = self.client.get('/permission/remove_role/%s' % latest_role.id)

        self.assertEqual(3, len(Role.objects.filter(company = company)))

    def test_add_role(self):
        response = self.client.post('/permission/add_role', { 'name' : 'test', 'permissions': ['Browse Assets'] })

        self.assertEqual(1, len(Role.objects.all().latest('created_date').permissions))