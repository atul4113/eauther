from src.libraries.utility.noseplugins import FormattedOutputTestCase
from src.lorepo.permission.models import Role, Permission
from src.lorepo.spaces.models import Space, SpaceAccess
from django.test.client import Client
from src.libraries.utility.test_assertions import status_code_for

class BasicTests(FormattedOutputTestCase):
    fixtures = ['permission_basic.json']

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        self.client.logout()

    def test_get_permissions(self):
        company = Space(title = 'company')
        role = Role(name = 'test',
                    permissions = [Permission.CONTENT_EDIT, Permission.ASSET_BROWSE],
                    company = company
                    )

        self.assertEqual([('Content', 'Create/Edit Lessons/Addons'), ('Assets', 'Browse Assets')], role.get_permissions())

    def test_create_company_will_create_correct_role_and_assign_to_space_access(self):
        self.client.login(username = 'kgebert', password = 'kgebert1')

        response = self.client.post('/corporate/create_company', { 'space' : 'test_space', 'user' : 'test' })

        status_code_for(response).should_be(302)
        latest_space_access = SpaceAccess.objects.all().latest('created_date')
        latest_role = Role.objects.all().latest('created_date')

        self.assertEqual(1, len(latest_space_access.roles))
        self.assertEqual([latest_role.pk], latest_space_access.roles)
        
    def test_lock_and_unlock_space_access_will_transfer_roles(self):
        space_access = SpaceAccess.objects.get(space__id = 12, user__id = 1)

        locked = space_access.lock()

        self.assertEqual(space_access.roles, locked.roles)

        unlocked = locked.unlock()

        self.assertEqual(unlocked.roles, locked.roles)

class AfterFixDb(FormattedOutputTestCase):
    fixtures = ['permission_manage_access.json']

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        self.client.logout()

    def test_space_access(self):
        space_access = SpaceAccess.objects.get(space__id = 12, user__id = 1)

        self.assertEqual('kgebert:Karol Corporation <owner>', space_access.__str__())

    def test_isOwner_true(self):
        space_access = SpaceAccess.objects.get(space__id = 12, user__id = 1)

        self.assertTrue(space_access.isOwner())

    def test_isOwner_false(self):
        space_access = SpaceAccess.objects.get(pk = 123)

        self.assertFalse(space_access.isOwner())