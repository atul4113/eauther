from src.libraries.utility.noseplugins import QueueTestCase
from django.test.client import Client
from src.libraries.utility.test_assertions import status_code_for

class SpaceAccessTests(QueueTestCase):
    fixtures = ['permission_views.json']

    def setUp(self):
        super(SpaceAccessTests, self).setUp()
        self.client = Client()
        
    def tearDown(self):
        super(SpaceAccessTests, self).tearDown()
        
    def test_one_user_trying_to_create_lesson_in_other_user_account(self):
        self.client.login(username = 'test', password = 'test')
        space_id = 3
        
        response = self.client.post('/mycontent/addcontent/%(space_id)s' % { 'space_id' : space_id },
                                    { 'next' : '/corporate/list/%(space_id)s' % { 'space_id' : space_id } })
        status_code_for(response).should_be(403)
        
    def test_one_user_trying_to_open_editor_with_lesson_from_other_user_account(self):
        self.client.login(username = 'test', password = 'test')
        content_id = 37
        
        response = self.client.get('/mycontent/%(content_id)s/editor?next=/mycontent' % { 'content_id' : content_id })
        status_code_for(response).should_be(403)

    def test_one_user_trying_to_see_other_user_lesson(self):
        self.client.login(username = 'test', password = 'test')
        content_id = 37
        
        response = self.client.get('/mycontent/view/%(content_id)s?next=/mycontent' % { 'content_id' : content_id })
        status_code_for(response).should_be(403)
        
    def test_one_user_trying_to_create_subspace_for_space_which_he_has_no_access(self):
        self.client.login(username = 'test', password = 'test')
        space_id = 3
        
        response = self.client.post('/spaces/add/%(space_id)s' % { 'space_id' : space_id })
        status_code_for(response).should_be(403)
        
    def test_one_user_trying_to_post_metadata_changes_on_lesson_from_other_user_account(self):
        self.client.login(username = 'test', password = 'test')
        content_id = 37
        
        response = self.client.post('/mycontent/%(content_id)s/metadata' % { 'content_id' : content_id },
                                    { 'next' : '/mycontent' })
        status_code_for(response).should_be(403)
        
    def test_one_user_trying_to_copy_lesson_to_space_without_permision(self):
        self.client.login(username = 'test', password = 'test')
        space_id = 20
        content_id = 68
        
        response = self.client.get('/mycontent/copy/%(content_id)s/%(space_id)s' % { 'content_id' : content_id, 'space_id' : space_id })
        status_code_for(response).should_be(403)

    def test_superuser_has_ability_to_copy(self):
        self.client.login(username = 'kgebert', password = 'kgebert1')
        space_id = 20 # space Publication 2 id, user should has permision here
        content_id = 68 
        
        response = self.client.get('/mycontent/copy/%(content_id)s/%(space_id)s' % { 'content_id' : content_id, 'space_id' : space_id }, follow = True)
        status_code_for(response).should_be(200)