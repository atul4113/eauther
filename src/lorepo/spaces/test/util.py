from django.contrib.auth.models import User
from lorepo.spaces.util import get_user_spaces, get_space_for_content,\
    filter_deleted, get_corporate_spaces_for_user, get_private_space_for_user,\
    get_spaces_tree, get_top_level_public_spaces, get_spaces_path_for_content,\
    is_space_owner, get_users_from_space, get_spaces_from_top_to_specific_space
from lorepo.mycontent.models import Content
from lorepo.spaces.models import Space
from libraries.utility.noseplugins import FormattedOutputTestCase

class UtilTest(FormattedOutputTestCase):
    fixtures = ['lorepo.json']

    def test_get_user_spaces(self):
        user = User(id=1, username='admin')
        spaces = get_user_spaces(user)
        self.assertEqual(len(spaces), 3, 'Not all spaces received for user admin')

    def test_get_space_for_content(self):
        content = Content.objects.get(pk=700)
        self.assertIsNotNone(content, 'Content with id=700 does not exists in fixture')

        space = get_space_for_content(content)
        self.assertIsNotNone(space, 'No private space found for content id=700')
        self.assertEqual('ala', space.title, 'Incorrect space returned for content id=700')

    def test_filter_deleted(self):
        user = User(id=1, username='admin')
        spaces = get_user_spaces(user)

        content_list, deleted, total = filter_deleted(spaces, subspaces=None, is_trash=False)
        self.assertEqual(27, len(content_list))
        self.assertEqual(27, total)

        content_list, deleted, total = filter_deleted(spaces, subspaces=None, is_trash=True)
        self.assertEqual(27, len(content_list))
        self.assertEqual(27, total)
        self.assertEqual(12, len(deleted))

    def test_get_corporate_spaces_for_user(self):
        user = User(id=1, username='admin')
        spaces = get_corporate_spaces_for_user(user)

        self.assertEqual(len(spaces), 1, 'Wrong number of spaces found')
        self.assertEqual(spaces.pop().title, 'Corporate', 'Wrong space found')

    def test_get_private_space_for_user(self):
        user = User(id=1, username='admin')
        space = get_private_space_for_user(user)

        self.assertIsNotNone(space, 'There should be at least one private space for user')
        self.assertEqual('admin', space.title)

    def test_get_spaces_tree(self):
        space_id = 772
        spaces = get_spaces_tree(space_id)

        self.assertEqual(len(spaces), 3, 'Not all spaces returned')

    def test_get_top_level_public_spaces(self):
        spaces = get_top_level_public_spaces()
        self.assertIsNotNone(spaces)
        self.assertEqual(len(spaces), 2)

    def test_get_spaces_path_for_content(self):
        content = Content.objects.get(pk=696)
        spaces = get_spaces_path_for_content(content, lambda space: space.is_public())
        self.assertEqual(len(spaces), 2)

        content = Content.objects.get(pk=4)
        spaces = get_spaces_path_for_content(content, lambda space: space.is_private())
        self.assertEqual(len(spaces), 2)

    def test_is_owner(self):
        user_aaa = User.objects.get(pk=204) # username aaa
        user_bbb = User.objects.get(pk=254) # username bbb

        space_aaa = Space.objects.get(pk=664)
        space_bbb = Space.objects.get(pk=666)

        self.assertTrue(is_space_owner(space_aaa, user_aaa))
        self.assertTrue(is_space_owner(space_bbb, user_bbb))
        self.assertFalse(is_space_owner(space_bbb, user_aaa))
        self.assertFalse(is_space_owner(space_aaa, user_bbb))
        
class GetUsersTest(FormattedOutputTestCase):
    fixtures = ['get_users.json']
    
    def test_get_users_from_space(self):
        project = Space.objects.get(pk=18)
        kgebert = User.objects.get(pk=3)
        owner1 = User.objects.get(pk=1)
        users = get_users_from_space(project)
        self.assertTrue(kgebert in users)
        self.assertTrue(owner1 in users)
        
        publication = Space.objects.get(pk=474)
        users = get_users_from_space(publication)
        self.assertTrue(owner1 in users)
        
    def test_get_spaces_from_top_to_specific_space(self):
        mauthor = Space.objects.get(pk=474)
        spaces = get_spaces_from_top_to_specific_space(mauthor)
        solwit = Space.objects.get(pk=18)
        solwit_hr = Space.objects.get(pk=23)
        
        self.assertTrue(solwit in spaces)
        self.assertTrue(mauthor in spaces)
        self.assertTrue(solwit_hr in spaces)