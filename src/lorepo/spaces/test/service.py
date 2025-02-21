from lorepo.spaces.models import Space
from libraries.utility.noseplugins import FormattedOutputTestCase
from lorepo.spaces.service import insert_space

class ServiceTest(FormattedOutputTestCase):
    def test_insert_space(self):
        company = Space(title='COMPANY')
        company.save()

        project = Space(title='PROJECT', parent=company)
        insert_space(project)

        from_db = Space.objects.get(pk=project.id)
        self.assertTrue(all([path_id for path_id in from_db.path]))