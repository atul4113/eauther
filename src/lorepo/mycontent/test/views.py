from django.test.client import Client
from lorepo.mycontent.models import Content, ContentType, CurrentlyEditing
from libraries.utility.noseplugins import FormattedOutputTestCase,\
    QueueTestCase
from xml.dom import minidom
from lorepo.mycontent.views import _get_title_for_editor
from lorepo.spaces.models import Space

class ViewsTests(QueueTestCase):
    fixtures = ['url.json']

    def setUp(self):
        super(ViewsTests, self).setUp()
        self.client = Client()
        self.client.login(username='kgebert', password='kgebert1')

    def tearDown(self):
        super(ViewsTests, self).tearDown()
        self.client.logout()

    def test_url_mycontent(self):
        response = self.client.get('/mycontent/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['is_trash'], False)
        self.assertEqual(len(response.context['contents']), 2)
        self.assertEqual(len(response.context['spaces']), 1)

    def test_url_mycontent_trash(self):
        response = self.client.get('/mycontent/395/trash/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['space_request'].id, 395)
        self.assertEqual(response.context['is_trash'], True)
        self.assertEqual(len(response.context['contents']), 3)

    def test_url_mycontent_preview(self):
        response = self.client.get('/mycontent/view/451')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['content'].id, 451)

    def test_url_mycontent_metadata(self):
        response = self.client.post('/mycontent/451/metadata', { "title" : "JavaEE", "tags" : "java", "description" : "java", "space_id" : 395, "next" : "/mycontent/395", "passing_score" : "55"})
        self.assertEqual(response.status_code, 302)
        content = Content.objects.get(pk=451)
        self.assertEqual(content.title, "JavaEE")
        self.assertEqual(content.content_type, ContentType.LESSON)
        self.assertEqual(response['location'], "http://testserver/mycontent/395")
        self.assertEqual(content.passing_score, 55)

        response = self.client.post('/mycontent/451/metadata', { "title" : "JavaEE", "tags" : "java", "description" : "java", "space_id" : 395, "next" : "/mycontent/395" , "is_template" : "on", "passing_score" : "55"})
        self.assertEqual(response.status_code, 302)
        content = Content.objects.get(pk=451)
        self.assertEqual(content.title, "JavaEE")
        self.assertEqual(content.content_type, ContentType.TEMPLATE)
        self.assertEqual(response['location'], "http://testserver/mycontent/395")

    def test_url_mycontent_metadata_with_public_space(self):
        response = self.client.post('/mycontent/451/metadata', { "title" : "JavaEE", "tags" : "java", "description" : "java", "space_id" : 395, "public_space_id" : 1398, "next" : "/mycontent/395", "passing_score" : "55"})
        self.assertEqual(response.status_code, 302)
        content = Content.objects.get(pk=451)
        self.assertEqual(content.title, "JavaEE")
        self.assertEqual(response['location'], "http://testserver/mycontent/395")

    def test_url_mycontent_makepublic(self):
        contentBefore = Content.objects.get(pk=451)
        '''
        Fixture url.json contain inconsistent public lesson data, so they're fixed by hand in tests
        ''' 
        contentBefore.is_public = True
        contentBefore.save()
        
        self.assertTrue(contentBefore.is_content_public())
        response = self.client.get('/mycontent/451/makepublic')
        contentAfter = Content.objects.get(pk=451)
        self.assertNotEqual(contentBefore.file, contentAfter.public_version)
        self.assertFalse(contentAfter.is_content_public())
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], "http://testserver/mycontent")

        contentBefore = Content.objects.get(pk=451)
        self.assertFalse(contentBefore.is_content_public())
        response = self.client.get('/mycontent/451/makepublic?next=/mycontent/111')
        contentAfter = Content.objects.get(pk=451)
        self.assertEqual(contentBefore.file, contentAfter.public_version)
        self.assertTrue(contentAfter.is_content_public())
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], "http://testserver/mycontent/111")


    def test_url_mycontent_maketemplate(self):
        contentBefore = Content.objects.get(pk=447)
        response = self.client.get('/mycontent/447/maketemplate')
        contentAfter = Content.objects.get(pk=447)
        self.assertNotEqual(contentBefore.content_type, contentAfter.content_type)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response._headers['location'], ('Location', "http://testserver/mycontent"))

        contentBefore = Content.objects.get(pk=447)
        response = self.client.get('/mycontent/447/maketemplate?next=/mycontent/111')
        contentAfter = Content.objects.get(pk=447)
        self.assertNotEqual(contentBefore.content_type, contentAfter.content_type)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response._headers['location'], ('Location', "http://testserver/mycontent/111"))

    def test_url_mycontent_delete(self):
        contentBefore = Content.objects.get(pk=447)
        content_spaceBefore = [content_space for content_space in contentBefore.contentspace_set.all() if not content_space.space.is_public()][0]
        response = self.client.get('/mycontent/447/delete?next=/mycontent/395')
        contentAfter = Content.objects.get(pk=447)
        content_spaceAfter = [content_space for content_space in contentAfter.contentspace_set.all() if not content_space.space.is_public()][0]
        self.assertNotEqual(content_spaceBefore.is_deleted, content_spaceAfter.is_deleted)
        self.assertNotEqual(contentBefore.modified_date, contentAfter.modified_date)
        self.assertFalse(contentAfter.is_content_public())
        self.assertEqual(contentAfter.content_type, ContentType.LESSON)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response._headers['location'], ('Location', "http://testserver/mycontent/395"))

class ActionsTests(QueueTestCase):
    fixtures = ['actions.json']

    def setUp(self):
        super(ActionsTests, self).setUp()
        self.client = Client()
        self.client.login(username='test', password='test')

    def tearDown(self):
        super(ActionsTests, self).tearDown()
        self.client.logout()

    def test_mycontent_copy_redirect(self):
        response = self.client.get('/mycontent/copy/7/3')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], "http://testserver/mycontent/3")

    def test_add_content(self):
        response = self.client.post('/mycontent/addcontent', { "title" : "Present Perfect", "tags" : "english,perfect", "description" : "present perfect", "score_type" : "last"})
        last_inserted = Content.objects.latest('modified_date')
        self.assertIsNotNone(last_inserted.file)
        self.assertEqual(last_inserted.file.version, 1)
        self.assertEqual(last_inserted.title, "Present Perfect")
        self.assertEqual(last_inserted.tags, "english,perfect")
        self.assertEqual(last_inserted.description, "present perfect")
        self.assertEqual(last_inserted.file.history_for, last_inserted)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], "http://testserver/mycontent/%(id)s/editor?new=1&next=/mycontent/" % {'id' : last_inserted.id})
        history = list(last_inserted.filestorage_set.all())
        self.assertEqual(len(history), 1)

        doc = minidom.parseString(last_inserted.file.contents)
        pages = doc.getElementsByTagName('page')
        self.assertEqual(len(pages), 1)
        self.assertNotEqual(pages[0].getAttribute('href'), '')

    def test_add_content_to_different_space(self):
        response = self.client.post('/mycontent/addcontent/3', { "title" : "Present Perfect", "tags" : "english,perfect", "description" : "present perfect", "score_type" : "last"})
        last_inserted = Content.objects.latest('modified_date')
        self.assertIsNotNone(last_inserted.file)
        self.assertEqual(last_inserted.file.version, 1)
        self.assertEqual(last_inserted.title, "Present Perfect")
        self.assertEqual(last_inserted.tags, "english,perfect")
        self.assertEqual(last_inserted.description, "present perfect")
        self.assertEqual(last_inserted.file.history_for, last_inserted)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], "http://testserver/mycontent/%(id)s/editor?new=1&next=/mycontent/" % {'id' : last_inserted.id})
        history = list(last_inserted.filestorage_set.all())
        self.assertEqual(len(history), 1)

    def test_add_content_with_template(self):
        self.client.post('/mycontent/addcontent', { "title" : "Present Perfect", "template" : "7", "score_type" : "last"})
        last_inserted = Content.objects.latest('modified_date')
        self.assertIsNotNone(last_inserted.file)
        self.assertEqual(last_inserted.file.version, 1)
        self.assertEqual(last_inserted.get_template().id, 7)

class HistoryTests(QueueTestCase):
    fixtures = ['history.json']

    def setUp(self):
        super(HistoryTests, self).setUp()
        self.client = Client()
        self.client.login(username='admin', password='admin')

    def tearDown(self):
        super(HistoryTests, self).tearDown()
        self.client.logout()

    # TODO fix test
    def _editor(self):
        content_before = Content.objects.get(pk=1200)
        history_before = list(content_before.filestorage_set.all())

        response = self.client.get('/mycontent/1200/editor')

        content_after = response.context['content']
        history_after = list(content_after.filestorage_set.all())

        self.assertGreater(content_after.modified_date, content_before.modified_date)
        self.assertEqual(len(history_after), len(history_before) + 1)

    # TODO fix test
    def _copy_content(self):
        self.client.get('/mycontent/copy/1200')
        copied_content = Content.objects.latest('modified_date')

        self.assertEqual(copied_content.file.version, 1)
        self.assertEqual(copied_content.file.history_for, copied_content)

    def test_show_history(self):
        response = self.client.get('/mycontent/1237/history')

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mycontent/history.html')

        self.assertIsNotNone(response.context['content'])
        self.assertIsNotNone(response.context['versions'])
        self.assertEqual(8, len(response.context['versions']))

    def test_set_version(self):
        response = self.client.get('/mycontent/1200/setversion/1204')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response._headers['location'], ('Location', "http://testserver/mycontent/1200/history"))

        content = Content.objects.get(pk=1200)
        self.assertEqual(content.file.id, 1204)
        self.assertEqual(content.file.version, 1)

class RedirectTest(QueueTestCase):
    fixtures = ['redirect.json']

    def setUp(self):
        super(RedirectTest, self).setUp()
        self.client = Client()
        self.client.login(username='test', password='test')

    def tearDown(self):
        super(RedirectTest, self).tearDown()
        self.client.logout()

    def test_after_delete_presentation(self):
        response = self.client.get('/mycontent/13/delete?next=/mycontent/3?page=2')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response._headers['location'], ('Location', "http://testserver/mycontent/3?page=2"))
    
    def test_after_copy_presentation(self):
        response = self.client.get('/mycontent/copy/13/3')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response._headers['location'], ('Location', "http://testserver/mycontent/3"))
    
    def test_paginator_with_wrong_page(self):
        response = self.client.get('/mycontent/3?page=0')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['current_page'].number, 1)
        
        response = self.client.get('/mycontent/3?page=-100')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['current_page'].number, 1)
        
        response = self.client.get('/mycontent/3?page=100')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['current_page'].number, 2)
        
class IsBeingEditedTest(QueueTestCase):
    fixtures = ['is_being_edited.json']

    def setUp(self):
        super(IsBeingEditedTest, self).setUp()
        self.client = Client()

    def tearDown(self):
        super(IsBeingEditedTest, self).tearDown()
        self.client.logout()

    def test_content_is_being_edited(self):
        self.client.login(username='test', password='test')
        response = self.client.get('/mycontent/41/editor')
        self.assertEqual(response.status_code, 200)
        currently_editing = CurrentlyEditing.objects.get(content=41)
        self.assertEqual(currently_editing.user.username, 'test')
        self.client.logout()
        self.client.login(username='test', password='test')
        response = self.client.get('/mycontent/41/editor')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mycontent/confirm_edit_content.html')
        self.assertEqual(response.context['username'], 'test')

    def test_exit_editor_is_deleting_current_content_record(self):
        self.client.login(username='test', password='test')
        response = self.client.get('/mycontent/45/editor')
        self.assertEqual(response.status_code, 200)
        currently_editing = CurrentlyEditing.objects.get(content=45)
        self.assertEqual(currently_editing.user.username, 'test')
        response = self.client.get('/mycontent/45/exit_editor')
        currently_editing = CurrentlyEditing.objects.filter(content=45)
        self.assertEqual(len(currently_editing), 0)

    def test_exit_editor_is_not_cleaning_all_records(self):
        self.client.login(username='test', password='test')
        response = self.client.get('/mycontent/45/editor')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/mycontent/49/editor')
        self.assertEqual(response.status_code, 200)
        currently_editing = CurrentlyEditing.objects.get(content=45)
        self.assertEqual(currently_editing.user.username, 'test')
        currently_editing = CurrentlyEditing.objects.get(content=49)
        self.assertEqual(currently_editing.user.username, 'test')
        response = self.client.get('/mycontent/45/exit_editor')
        currently_editing = CurrentlyEditing.objects.filter(content=45)
        self.assertEqual(len(currently_editing), 0)
        currently_editing = CurrentlyEditing.objects.get(content=49)
        self.assertEqual(currently_editing.user.username, 'test')
        
class EditorTitleTest(FormattedOutputTestCase):
    fixtures = ['editor_title.json']
    
    def test_content_in_my_content(self):
        space = Space.objects.get(pk=4)
        content = Content.objects.get(pk=10204)
        
        title = _get_title_for_editor(content, space)
        
        expected_title = '<b>Lesson:</b> 3D Viewer Presentation (Development) | <b>Template:</b> None'
        self.assertEqual(title['title'], expected_title)
        
    def test_corporate_content_in_publication_root(self):
        space = Space.objects.get(pk=9759)
        content = Content.objects.get(pk=9781)
        
        title = _get_title_for_editor(content, space)
        
        expected_title = '<b>Project:</b> Dragonia project | <b>Publication:</b> Public'
        expected_subtitle = '<b>Lesson:</b> [LEA-2490] Working with Surveys and Survey Data  | <b>Template:</b> None'
        
        self.assertEqual(title['title'], expected_title)
        self.assertEqual(title['sub_title'], expected_subtitle)
        
    def test_corporate_content_in_chapter(self):
        space = Space.objects.get(pk=9943)
        content = Content.objects.get(pk=9949)
        
        title = _get_title_for_editor(content, space)
        
        expected_title = '<b>Project:</b> Dragonia project | <b>Publication:</b> Public'
        expected_subtitle = '<b>Lesson:</b> Lesson in Course 01 | <b>Template:</b> [LEA-2490] Working with Surveys and Survey Data '
        
        self.assertEqual(title['title'], expected_title)
        self.assertEqual(title['sub_title'], expected_subtitle)
        
    def test_corporate_content_in_subchapter(self):
        space = Space.objects.get(pk=9945)
        content = Content.objects.get(pk=9954)
        
        title = _get_title_for_editor(content, space)
        
        expected_title = '<b>Project:</b> Dragonia project | <b>Publication:</b> Public'
        expected_subtitle = '<b>Lesson:</b> Lesson in Course 01 / sub 0 | <b>Template:</b> None'
        
        self.assertEqual(title['title'], expected_title)
        self.assertEqual(title['sub_title'], expected_subtitle)
        
    def test_corporate_content_in_subsubchapter(self):
        space = Space.objects.get(pk=9946)
        content = Content.objects.get(pk=9959)
        
        title = _get_title_for_editor(content, space)
        
        expected_title = '<b>Project:</b> Dragonia project | <b>Publication:</b> Public'
        expected_subtitle = '<b>Lesson:</b> Lesson in Course 01 / sub / sub | <b>Template:</b> None'
        
        self.assertEqual(title['title'], expected_title)
        self.assertEqual(title['sub_title'], expected_subtitle)