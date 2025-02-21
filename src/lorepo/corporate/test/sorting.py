from libraries.utility.noseplugins import FormattedOutputTestCase
from libraries.utility.test_assertions import the
from lorepo.corporate.utils import get_contents
from lorepo.spaces.models import Space

class SortingTests(FormattedOutputTestCase):
    fixtures = ['libraries.testing.spaces.json', 'libraries.testing.users.json', 'libraries.testing.mycontent.json']
    
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
    
    def test_sorting_by_title_asc(self):
        spaces = Space.objects.get(pk=1)
        contents = get_contents(spaces, is_trash=False, order_by='title')
        the(contents).length_is(4)
        the(contents[0].title).equals('Animals and Plants Cells')
    
    def test_sorting_by_title_desc(self):
        spaces = Space.objects.get(pk=1)
        contents = get_contents(spaces, is_trash=False, order_by='-title')
        the(contents).length_is(4)
        the(contents[0].title).equals('Zoo and Farm')
    
    def test_sorting_by_date_asc(self):
        spaces = Space.objects.get(pk=1)
        contents = get_contents(spaces, is_trash=False, order_by='modified_date')
        the(contents).length_is(4)
        the(contents[0].title).equals('Linear Algebra')
    
    def test_sorting_by_date_desc(self):
        spaces = Space.objects.get(pk=1)
        contents = get_contents(spaces, is_trash=False, order_by='-modified_date')
        the(contents).length_is(4)
        the(contents[0].title).equals('Building blocks')