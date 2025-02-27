from src.libraries.utility.noseplugins import FormattedOutputTestCase
from django.test.client import Client
from src.lorepo.spaces.models import SpaceAccess, LockedSpaceAccess
from src.lorepo.spaces.util import get_spaces_tree

class LockingCompanyTests(FormattedOutputTestCase):
    fixtures = ['locking_company_fix.json']
    
    def setUp(self):
        self.client = Client()
        self.client.login(username='kgebert', password='kgebert1')

    def tearDown(self):
        self.client.logout()
    
    def test_lock_company_will_create_locked_space_accesses(self):
        spaces = get_spaces_tree(8)
        space_accesses_before = []
        space_accesses_after = []
        locked_space_accesses = []
        
        for space in spaces:
            space_accesses_before.extend( SpaceAccess.objects.filter(space = space) )
            
        self.assertEqual(2, len(space_accesses_before), 'Two users should have access to company with id 8')
        
        self.client.get('/company/lock/8')
        
        for space in spaces:
            space_accesses_after.extend( SpaceAccess.objects.filter(space = space) )
            locked_space_accesses.extend( LockedSpaceAccess.objects.filter(space = space) )
        
        self.assertEqual(0, len(space_accesses_after), 'Space Accesses should be removed')
        self.assertEqual(2, len(locked_space_accesses), '2 Locked Space Accesses should be created')
        
        self.assertEqual(space_accesses_before[0].access_right, locked_space_accesses[0].access_right, '')
    
    def test_unlock_company_will_recreate_space_accesses(self):
        spaces = get_spaces_tree(23)
        space_accesses_before = []
        space_accesses_after = []
        locked_space_accesses_before = []
        locked_space_accesses_after = []
        
        for space in spaces:
            space_accesses_before.extend( SpaceAccess.objects.filter(space = space) )
            locked_space_accesses_before.extend( LockedSpaceAccess.objects.filter(space = space) )
            
        self.assertEqual(1, len(locked_space_accesses_before), 'One user should have locked access to company with id 23')
        self.assertEqual(0, len(space_accesses_before), 'There should be none space access to company with id 23')
        
        self.client.get('/company/unlock/23')
        
        for space in spaces:
            locked_space_accesses_after.extend( LockedSpaceAccess.objects.filter(space = space) )
            space_accesses_after.extend( SpaceAccess.objects.filter(space = space) )
            
        self.assertEqual(0, len(locked_space_accesses_after), 'There should be none locked space access to company with id 23')
        self.assertEqual(1, len(space_accesses_after), 'One user should have access to company with id 23')
    
    def test_locked_company_user_will_see_message_after_login(self):
        self.client.logout()
        self.client = Client()
        self.client.login(username='locked_company_admin', password='admin')
        
        response = self.client.get('/corporate', follow = True)
        self.assertContains(response, 'The company account &quot;locked_company&quot; has been locked. Please contact administrator')
