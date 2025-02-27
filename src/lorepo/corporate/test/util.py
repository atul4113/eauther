from src.lorepo.spaces.models import Space
from src.lorepo.spaces.util import get_spaces_subtree
from src.lorepo.corporate.utils import get_division_for_space,\
    get_contents_from_company, get_publication_for_space
from src.libraries.utility.noseplugins import FormattedOutputTestCase
from src.lorepo.mycontent.models import ContentType

class CorporateUtilTest(FormattedOutputTestCase):
    fixtures = ['util.json']

    def test_get_division_for_space(self):
        space = Space.objects.get(pk=376)
        spaces = get_spaces_subtree(space.id)
        projects = [space for space in spaces if space.parent.is_second_level()]

        for project in projects:
            division = get_division_for_space(project)
            self.assertEqual(division.id, 376)
            
    def test_get_publication_for_space(self):
        space = Space.objects.get(pk=449)
        
        publication = get_publication_for_space(space)
        
        self.assertEqual(publication.id, 449) #passed space is top-level publication
        
    def test_get_publication_for_space_with_chapters(self):
        space = Space.objects.get(pk=564)
        
        publication = get_publication_for_space(space)
        
        self.assertEqual(publication.id, 564)
        
    def test_get_publication_for_space_with_sub_chapters(self):
        space = Space.objects.get(pk=565)
        
        publication = get_publication_for_space(space)
        
        self.assertEqual(publication.id, 564)
        
            
class DashBoardContents(FormattedOutputTestCase):
    fixtures = ['dashboard_contents.json']
    
    def test_get_templates_from_company(self):
        kgebert_company = Space.objects.get(pk=31)
        templates = get_contents_from_company(kgebert_company, lambda content: content.content_type == ContentType.TEMPLATE)
        templates_ids = [template.id for template in templates]
        templates_ids_in_company = [47, 2299, 2288]
        
        for template_id in templates_ids_in_company:
            self.assertIn(template_id, templates_ids)