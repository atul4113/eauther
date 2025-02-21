from lorepo.mycontent.util import get_contents_from_space,\
    get_contents_from_public_space, get_contents_from_specific_space
from lorepo.spaces.models import Space
from libraries.utility.noseplugins import FormattedOutputTestCase
from django.test.client import Client
from libraries.utility.test_assertions import the
from lorepo.mycontent.models import Content


class UtilTests(FormattedOutputTestCase):
    fixtures = ['public_spaces.json']

    def test_get_contents_from_space(self):
        space = Space.objects.get(pk=761)
        contents = get_contents_from_space(space)
        self.assertIsNotNone(contents)
        self.assertEqual(len(contents), 2)

        space = Space.objects.get(pk=748)
        contents = get_contents_from_space(space)
        self.assertIsNotNone(contents)
        self.assertEqual(len(contents), 37)

    def test_get_contents_from_public_space(self):
        space = Space.objects.get(pk=761)
        
        '''
        Fixture public_spaces.json contain inconsistent public lesson data, so they're fixed by hand in tests
        ''' 
        content = Content.objects.get(pk=793)
        content.is_public = True
        content.save()
        content = Content.objects.get(pk=823)
        content.is_public = True
        content.save()
        
        contents = get_contents_from_public_space(space)
        self.assertIsNotNone(contents)
        self.assertEqual(len(contents), 2)

    def test_get_contents_from_public_space_negative(self):
        space = Space.objects.get(pk=748)
        self.assertRaises(Exception, get_contents_from_public_space, space)

class UtilTests2(FormattedOutputTestCase):
    fixtures = ['user.json']

    def test_get_contents_from_specific_space(self):
        space = Space.objects.get(pk=398)
        contents = get_contents_from_specific_space(space.id)
        self.assertIsNotNone(contents)
        self.assertEqual(len(contents), 1)

        space = Space.objects.get(pk=395)
        contents = get_contents_from_specific_space(space.id)
        self.assertIsNotNone(contents)
        self.assertEqual(len(contents), 14)

        space = Space.objects.get(pk=606)
        contents = get_contents_from_specific_space(space.id)
        self.assertIsNotNone(contents)
        self.assertEqual(len(contents), 1)

        space = Space.objects.get(pk=606)
        contents = get_contents_from_specific_space(space.id)
        space2 = Space.objects.get(pk=398)
        contents.extend(get_contents_from_specific_space(space2.id))
        self.assertIsNotNone(contents)
        self.assertEqual(len(contents), 2)

class WhoIsEditingTests(FormattedOutputTestCase):
    fixtures = ['who_is_editing.json']

    def setUp(self):
        super(WhoIsEditingTests, self).setUp()
        self.client = Client()
        self.client.login(username='kgebert', password='kgebert1')

    def tearDown(self):
        super(WhoIsEditingTests, self).tearDown()
        self.client.logout()

    def test_no_one_is_using_editor(self):
        content = Content.objects.get(pk=5981343255101440)
        current_user = content.who_is_editing()
        the(current_user).is_none()

    def test_some_one_is_using_editor(self):
        content = Content.objects.get(pk=5981343255101440)
        self.client.get('/mycontent/5981343255101440/editor')
        current_user = content.who_is_editing()
        the(current_user.username).equals('kgebert')

    def test_no_cross_information(self):
        self.client.get('/mycontent/5981343255101440/editor')
        content = Content.objects.get(pk=5242471441235968)
        current_user = content.who_is_editing()
        the(current_user).is_none()