# -*- coding: utf-8 -*-
from django.test.client import Client, RequestFactory
from src.lorepo.spaces.models import Space
from src.lorepo.mycontent.models import Content, ContentSpace, SpaceTemplate
from src.libraries.utility.noseplugins import FormattedOutputTestCase
from src.libraries.utility.test_assertions import status_code_for
from django.contrib.auth.models import User
from src.lorepo.corporate.views import get_publications_for_project_json

class CorporateLogoTest(FormattedOutputTestCase):
    fixtures = ['logo.json']

    def setUp(self):
        self.client = Client()

    def test_home_logo_for_user_with_logo(self):
        self.client.login(username='kgebert', password='kgebert1')
        response = self.client.get('/corporate/')
        self.assertContains(response, 'src="/file/serve/103"')
        self.assertContains(response, '<a href="/corporate" title="Dashboard"')

    def test_home_logo_for_user_without_logo(self):
        self.client.login(username='karol2', password='karol')
        response = self.client.get('/corporate/')
        self.assertContains(response, 'src="/media/images/main-page/ma_main_mauthor_logo.svg"')
        self.assertContains(response, '<a href="/corporate">Dashboard</a>')

    def test_home_logo_for_not_logged_user(self):
        response = self.client.get('/')
        self.assertContains(response, 'src="/media/images/main-page/ma_main_mauthor_logo.svg"')
        self.assertContains(response, '<a href="/" title="Home"')

    def test_upload_logo_when_user_is_not_corporate_space_owner(self):
        self.client.login(username='karol', password='karol')
        response = self.client.get('/corporate/upload')
        self.assertEqual(response.status_code, 403)

    def test_upload_logo_when_user_is_corporate_space_owner(self):
        self.client.login(username='kgebert', password='kgebert1')
        response = self.client.get('/corporate/upload')
        self.assertEqual(response.status_code, 200)

class ViewsTest(FormattedOutputTestCase):
    fixtures = ['corporate.json']

    def setUp(self):
        super(ViewsTest, self).setUp()
        self.client = Client()
        self.client.login(username='test', password='test')

    def tearDown(self):
        super(ViewsTest, self).tearDown()
        self.client.logout()

    # division without projects should not be displayed in drop-down-list
    def test_copy_to_location_division_without_projects(self):
        response = self.client.get('/corporate/view/36')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['divisions']), 1)

    def test_simple_rename_project(self):
        response = self.client.get('/corporate/32/rename_space')
        self.assertEqual(response.status_code, 200)

    def test_copy_to_account(self):
        cs_before = ContentSpace.objects.count()
        self.client.post('/corporate/copy_to_account/36', {'user' : 'admin'})
        cs_after = ContentSpace.objects.count()
        self.assertEqual(cs_after, cs_before + 1)

class PublishTest(FormattedOutputTestCase):
    fixtures = ['publish.json']

    def setUp(self):
        super(PublishTest, self).setUp()
        self.factory = RequestFactory()
        self.client = Client()
        self.client.login(username='owner1', password='owner1')

    def tearDown(self):
        super(PublishTest, self).tearDown()
        self.client.logout()

    def test_publish_corporate_content(self):
        # FIXME uzupełnić testy
        response = self.client.get('/corporate/375/makepublic?next=/corporate/list/372') # unpublish
        self.assertEqual(response.status_code, 302)
        content = Content.objects.get(pk=375)
        self.assertTrue(content.is_content_public())
        self.assertTrue(content.is_public)
        self.assertIsNotNone(content.public_version_id)

        response = self.client.get('/corporate/375/makepublic?next=/corporate/list/372') # publish
        self.assertEqual(response.status_code, 302)
        content = Content.objects.get(pk=375)
        self.assertFalse(content.is_content_public())
        self.assertFalse(content.is_public)
        self.assertIsNone(content.public_version_id)

    def test_fixdb_public_content(self):
        response = self.client.get('/corporate/fixdb_public_content')
        self.assertEqual(response.status_code, 302)
        public_contents = Content.objects.filter(is_public=True)
        for content in public_contents:
            content_spaces = ContentSpace.objects.filter(content=content)
            self.assertEqual(len(content_spaces), 2)
    
    def test_publish_corporate_content_with_inconsistent_meta(self):
        content = Content.objects.get(pk=375)
        content.public_version_id = 374
        content.is_public = False
        content.save()
        
        response = self.client.get('/corporate/375/makepublic?next=/corporate/list/372') # unpublish
        self.assertEqual(response.status_code, 302)
        content = Content.objects.get(pk=375)
        self.assertFalse(content.is_content_public())
        self.assertFalse(content.is_public)
        self.assertIsNone(content.public_version_id)
        
    def test_fixdb_projects(self):
        spaces = Space.objects.all()
        divisions = [space for space in spaces if space.is_second_level()]
        response = self.client.get('/corporate/fixdb_projects')
        self.assertEqual(response.status_code, 302)
        contents = []
        for division in divisions:
            self.assertGreater(len(division.kids.all()), 0)
            for cs in division.contentspace_set.all():
                contents.append(cs.content)
        
        self.assertEqual(len(contents), 0)
        
class ProjectsTest(FormattedOutputTestCase):
    fixtures = ['projects.json']

    def setUp(self):
        self.client = Client()
        self.client.login(username='owner1', password='owner1')

    def tearDown(self):
        self.client.logout()
        
    
    def test_selected_space(self):
        response = self.client.get('/corporate/list/449')
        self.assertEqual(response.context['space_request'].id, 449)
        response = self.client.get('/corporate/list/256')
        self.assertEqual(response.context['space_request'].id, 449)
        self.assertEqual(len(response.context['contents']), 0)

    def test_if_metadata_contains_projects(self):
        response = self.client.get('/corporate/443/metadata?next=/corporate/list/256')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['projects']), 3)

    def test_archive_project(self):
        response = self.client.get('/corporate/projects/376')
        self.assertEqual(len(response.context['spaces']), 1) # space.id = 377
        response = self.client.get('/corporate/377/delete_project?next=/corporate/projects/376', follow=True)
        self.assertEqual(len(response.context['spaces']), 0) # space.id = 377
        response = self.client.get('/corporate/projects/376?archived=1')
        self.assertEqual(len(response.context['spaces']), 1)

    def test_count_of_projects(self):
        response = self.client.get('/corporate/projects/376')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['spaces']), 1)

    def test_rename_project(self):
        response = self.client.post('/corporate/projects/377/rename_project', {'title' : 'changed name', 'next' : '/corporate/projects/376'})
        self.assertEqual(response.status_code, 302)
        space = Space.objects.get(pk=377)
        self.assertEqual(space.title, 'changed name')

    def test_table_of_contents_count(self):
        response = self.client.get('/corporate/377/subproject')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['spaces']), 0)
        self.assertIsNotNone(response.context['project'])

class Projects2Test(FormattedOutputTestCase):
    fixtures = ['projects2_new.json']
    
    def setUp(self):
        self.client = Client()
        self.client.login(username='kgebert', password='kgebert1')

    def tearDown(self):
        self.client.logout()

    def test_add_section(self):
        response = self.client.get('/corporate/6509108836433920/add_subproject?project=5136918324969472')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], "http://testserver/corporate/5136918324969472/subproject")

class DeleteContentTest(FormattedOutputTestCase):
    fixtures = ['delete_content.json']

    def setUp(self):
        self.client = Client()
        self.client.login(username='admin', password='admin')

    def tearDown(self):
        self.client.logout()

    # FIXME. Potrzebny nowy zrzut bazy z uwzglednieniem spaces_path
    def _deleted_and_restore_content(self):
        response = self.client.get('/corporate/list/14')
        self.assertEqual(response.status_code, 200)
        response = self.client.post('/mycontent/addcontent/14', {'title' : 'delete_content'})
        response = self.client.get('/corporate/list/14')
        self.assertEqual(len(response.context['contents']), 2)
        content = Content.objects.latest('modified_date')
        response = self.client.get('/corporate/' + str(content.id) + '/delete?next=/corporate/list/14', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['contents']), 1)
        response = self.client.get('/corporate/list/14/trash')
        self.assertEqual(len(response.context['contents']), 1)
        response = self.client.get('/corporate/'+ str(content.id) +'/delete?next=/corporate/list/14/trash', follow=True)
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/corporate/list/14')
        self.assertEqual(len(response.context['contents']), 2)

class AccessToProjectTest(FormattedOutputTestCase):
    
    fixtures = ['access_to_project.json']

    def setUp(self):
        self.client = Client()
        self.client.login(username='Pracownik', password='pracownik')

    def tearDown(self):
        self.client.logout()
        
    def test_simple_get_list(self):
        response = self.client.get('/corporate/list/12')
        self.assertEqual(response.status_code, 200)
        
    def test_projects_count(self):
        response = self.client.get('/corporate/list/12')
        self.assertEqual(len(response.context['spaces']), 1) # user Pracownik has access only to Projekt 3
        
class PublicCategories(FormattedOutputTestCase):
    
    fixtures = ['public_categories.json']

    def setUp(self):
        super(PublicCategories, self).setUp()
        self.client = Client()
        self.client.login(username='kgebert', password='kgebert1')
     
    def tearDown(self):
        super(PublicCategories, self).tearDown()
        
    def test_rename_public_category(self):
        response = self.client.post('/spaces/22/rename_public?next=/corporate/publicspaces', {'title' : 'pygame rename'})
        self.assertEqual(response.status_code, 302)
        space = Space.objects.all().latest('modified_date')
        self.assertEqual(space.title, 'pygame rename')
        
    def test_add_subcategory(self):
        response = self.client.get('/spaces/25/subspace', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['spaces']), 2)
        
    def test_change_content_space_when_removing_public_category(self):
        space = Space.objects.get(pk=25)
        content = Content.objects.get(pk=16)
        cs = ContentSpace.objects.filter(space=space, content=content)
        self.assertEqual(len(cs), 1)
        response = self.client.get('/spaces/25/delete_public?next=/corporate/publicspaces')
        cs = ContentSpace.objects.filter(space=space, content=content)
        self.assertEqual(len(cs), 0)
        new_space = Space.objects.get(pk=24)
        new_cs = ContentSpace.objects.filter(space=new_space, content=content)
        self.assertEqual(len(new_cs), 1)

class ChangeTemplateTests(FormattedOutputTestCase):
    fixtures = ['change_template.json']

    def setUp(self):
        self.client = Client()
        self.client.login(username='owner1', password='owner1')

    def tearDown(self):
        self.client.logout()

    def test_access_to_change_template_view(self):
        response = self.client.get('/corporate/change_template') # logged as admin
        status_code_for(response).should_be(200)

        self.client.logout()
        response = self.client.get('/corporate/change_template') # not logged in
        status_code_for(response).should_be(302)

        self.client.logout()
        self.client.login(username='kgebert', password='kgebert1')
        response = self.client.get('/user/change_template') # logged as user who has no company
        status_code_for(response).should_be(404)

    def test_change_info(self):
        response = self.client.post('/corporate/change_template', {'template' : 884})
        self.assertContains(response, "Default template changed.")
        self.assertContains(response, "checked")

    def test_change_template_by_two_diffrent_companies(self):
        self.client.post('/corporate/change_template', { 'template' : 884})
        st = SpaceTemplate.objects.count()
        self.assertEqual(st, 1)
        self.client.logout()
        self.client.login(username='test', password='test')
        self.client.post('/corporate/change_template', { 'template' : 1074})
        st = SpaceTemplate.objects.count()
        self.assertEqual(st, 2)
        
    def test_delete_default_template(self):
        self.client.post('/corporate/change_template', { 'template' : 884})
        space_template_count_before = len(SpaceTemplate.objects.filter(space__id=18))
        self.assertEqual(space_template_count_before, 1)
        self.client.post('/corporate/change_template', { 'template' : 'none'})
        space_template_count_after = len(SpaceTemplate.objects.filter(space__id=18))
        self.assertEqual(space_template_count_after, 0)
        
    def test_delete_default_template_when_template_is_not_set(self):
        space_template_count_before = len(SpaceTemplate.objects.filter(space__id=18))
        self.assertEqual(space_template_count_before, 0)
        self.client.post('/corporate/change_template', { 'template' : 'none'})
        space_template_count_after = len(SpaceTemplate.objects.filter(space__id=18))
        self.assertEqual(space_template_count_after, 0)
        
class NewEditMetadataTests(FormattedOutputTestCase):
    fixtures = ['space_level.json']

    PROJECT_ID = 5488762045857792

    class Request(object):
        def __init__(self, project_id, user):
            self.GET = { 'projectId' : project_id }
            self.user = user

    def setUp(self):
        self.client = Client()
        self.client.login(username='kgebert', password='kgebert1')

    def tearDown(self):
        self.client.logout()

    def test_get_publications_json_renders_correct(self):
        user = User.objects.get(username = 'kgebert')
        request = self.Request(self.PROJECT_ID, user)
        response = get_publications_for_project_json(request)
        import json
        json = json.loads(response.content)
        
        self.assertEqual(len(json['publications']), 1)
        self.assertEqual(json['publications'][0]['id'], '6614661952700416')
        self.assertEqual(json['publications'][0]['title'], 'Publication 1')