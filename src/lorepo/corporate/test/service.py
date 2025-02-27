from src.libraries.utility.noseplugins import FormattedOutputTestCase
from django.test.client import Client
from src.lorepo.spaces.models import Space
from src.lorepo.spaces.service import insert_space, update_space

class SpaceAccessTests(FormattedOutputTestCase):
    fixtures = ['space_service.json']

    def setUp(self):
        self.client = Client()

    def test_insert_space_create_path_including_all_spaces_within_inserted_space(self):
        space_parent = Space.objects.get(pk = 5488762045857792)
        space = Space(title = 'test', parent = space_parent)

        insert_space(space)

        self.assertEqual([5770237022568448, 5488762045857792, space.pk], space.path)
        
    def test_update_space_uses_insert_space_not_space_save_so_the_space_path_is_updated(self):
        space = Space(title = 'test')

        update_space(space)

        self.assertEqual([space.pk], space.path)