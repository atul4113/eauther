from src.libraries.utility.noseplugins import FormattedOutputTestCase
from src.lorepo.mycontent.models import Content, ContentSpace
from src.lorepo.spaces.models import Space
from src.lorepo.mycontent.service import add_content_to_space, remove_content_space,\
    _update_contents_count
from django.contrib.auth.models import User

class ContentsCounterTest(FormattedOutputTestCase):
    fixtures = ['contents_counter.json']

    def setUp(self):
        super(ContentsCounterTest, self).setUp()

    def tearDown(self):
        super(ContentsCounterTest, self).tearDown()

    """
    # test with DatabaseError: the id allocated for a new entity was already in use, please try again
    def test_add_content_to_space_increment_counter_properly(self):
        user = User.objects.get(username='kgebert')
        content = Content.objects.get(pk=840)
        copy = content.makeCopy(user)
        space_before = Space.objects.filter(pk=732)[0]
        self.assertEqual(1, space_before.contents_count)
        cs = add_content_to_space(copy, space_before)
        space_after = Space.objects.filter(pk=732)[0]
        self.assertEqual(2, space_after.contents_count)
    """

    def test_remove_content_from_space_decrement_counter_properly(self):
        content = Content.objects.filter(pk=840)[0]
        space_before = Space.objects.filter(pk=732)[0]
        cs = ContentSpace.objects.filter(space=space_before, content=content)[0]
        self.assertEqual(1, space_before.contents_count)
        remove_content_space(cs)
        space_after = Space.objects.filter(pk=732)[0]
        self.assertEqual(0, space_after.contents_count)
        
    def test_update_contents_count(self):
        spaces_id = ['732']
        _update_contents_count(spaces_id, lambda x: x + 1)
        space = Space.objects.filter(pk=732)[0]
        self.assertEqual(2, space.contents_count)