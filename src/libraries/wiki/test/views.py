# -*- coding: utf-8 -*-
from django.test.client import Client
from src.libraries.wiki.models import WikiPage, WikiFile
from src.libraries.wiki.forms import WikiPageForm
from django.contrib.auth.models import User
from src.libraries.utility.noseplugins import FormattedOutputTestCase
from src.libraries.utility.test_assertions import status_code_for, the

class ViewsTest(FormattedOutputTestCase):
    fixtures = ['wiki.json']

    def setUp(self):
        self.client = Client()
        self.client.login(username='kgebert', password='kgebert1')

    def test_wiki_paths(self):
        response = self.client.get('/doc/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Help")

        response = self.client.get('/doc/page/Heniek')
        self.assertEqual(response.status_code, 302)

        response = self.client.get('/doc/page/Heniek', follow=True)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.redirect_chain, [('http://testserver/doc/add?title=Heniek', 302)])
        self.assertEqual(response.context['title'], 'Heniek')
        self.assertContains(response, 'This page doesn\'t exist yet. You can create it here.')
        self.assertContains(response, "Markdown syntax")

        response = self.client.get('/doc/add')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Markdown syntax")

    def test_wiki_add_positive(self):
        response = self.client.post('/doc/add?title=Heniek', {'id' : '', 'title' : 'Heniek','text' : 'jakis text'})
        self.assertEqual(response.status_code, 302)
        wp = WikiPage.objects.get(title='Heniek')
        self.assertIsNotNone(wp)
        self.assertEqual(response['Location'], "http://testserver/doc")

    def test_wiki_add_unauthorized(self):
        self.client.logout()
        self.client.login(username='karol', password='karol1')
        response = self.client.get('/doc/add?title=test123')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], "http://testserver/accounts/login/?next=/doc/add%3Ftitle%3Dtest123")

    def test_wiki_add_missing_title(self):
        response = self.client.post('/doc/add?title=Heniek', {'id' : '', 'title' : '','text' : 'jakis text'})
        self.assertEqual(response.status_code, 200)
        pages = WikiPage.objects.filter(title='Heniek')
        self.assertEqual(len(pages), 0)

    def test_wiki_form_positive(self):
        form = WikiPageForm({'id' : '', 'title' : 'Heniek', 'text' : 'jakiś text'})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.errors, {})

    def test_wiki_form_negative(self):
        form = WikiPageForm({'id' : '', 'title' : '', 'text' : 'jakiś text'})
        self.assertFalse(form.is_valid())
        self.assertNotEqual(form.errors, {})

        form = WikiPageForm({'id' : '','title' : 'Henik', 'text' : ''})
        self.assertFalse(form.is_valid())
        self.assertNotEqual(form.errors, {})

    def test_wiki_edit_positive(self):
        response = self.client.post('/doc/edit/586', {'id' : '586', 'title' : 'Ziutek', 'text' : 'smth here' })
        self.assertEqual(response.status_code, 302)
        wp = WikiPage.objects.get(pk=586)
        self.assertEqual(wp.title, 'Ziutek')
        self.assertEqual(response['Location'], "http://testserver/doc/page/Ziutek")

    def test_wiki_edit_unauthorized(self):
        self.client.logout()
        self.client.login(username='karol', password='karol1')
        response = self.client.get('/doc/edit/586')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], "http://testserver/accounts/login/?next=/doc/edit/586")

    def test_wiki_edit_no_changes(self):
        response = self.client.post('/doc/edit/586', {'id' : '586', 'title' : 'Help', 'text' : 'U can get help here' })
        self.assertEqual(response.status_code, 302)
        wp = WikiPage.objects.get(pk=586)
        self.assertEqual(wp.title, 'Help')

    def test_wiki_edit_negative(self):
        user = User.objects.get(pk=6)
        wp = WikiPage(pk=12345, title='Info', text='some text', author=user, url='Info')
        wp.save()
        response = self.client.post('/doc/edit/586', {'id' : '586', 'title' : 'Info', 'text' : 'U can get help here' })
        self.assertEqual(response.status_code, 200)

    def test_wiki_upload_logout(self):
        self.client.logout()
        response = self.client.get('/doc/upload')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], "http://testserver/accounts/login/?next=/doc/upload")

    def test_wiki_upload_empty_file(self):
        response = self.client.post('/doc/upload?next=/doc', {'next' : '/doc'})
        self.assertEqual(response.status_code, 302)
        wf = WikiFile.objects.all()
        self.assertEqual(response['location'], "http://testserver/doc/upload?next=/doc")
        self.assertEqual(len(wf), 0)

    def test_wiki_indexPage_with_no_wiki(self):
        WikiPage.objects.all().delete()
        response = self.client.get('/doc/page/index', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wiki/addpage.html")

    def test_wiki_indexPage_with_no_wiki_and_no_access(self):
        WikiPage.objects.all().delete()
        user = User.objects.get(pk=6)
        user.is_staff = False
        user.is_superuser = False
        user.save()
        response = self.client.get('/doc/page/index', follow=True)
        self.assertEqual(response.status_code, 404)

    def test_preview_page_negative(self):
        response = self.client.get('/doc/preview')
        self.assertEqual(response.status_code, 404)

    def test_preview_page_positive(self):
        response = self.client.post('/doc/preview', {"title" : "Test Page", "text" : "**emphasized text** and some normal one"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Page")
        self.assertContains(response, "<strong>emphasized text</strong> and some normal one")


class DeletionTests(FormattedOutputTestCase):
    fixtures = ['wiki_delete.json']

    def setUp(self):
        self.client = Client()
        self.client.login(username='admin', password='admin')

    def test_delete_wiki_positive(self):
        wiki_pages = WikiPage.objects.count()
        response = self.client.get('/doc/delete/10')
        status_code_for(response).should_be(302)
        wiki_pages_after = WikiPage.objects.count()
        self.assertNotEqual(wiki_pages, wiki_pages_after)

    def test_delete_wiki_negative(self):
        wiki_pages = WikiPage.objects.count()
        response = self.client.get('/doc/delete/1586') # this wiki doesn't exist so this action should raise 404
        status_code_for(response).should_be(404)
        wiki_pages_after = WikiPage.objects.count()
        self.assertEqual(wiki_pages, wiki_pages_after)

    def test_delete_wiki_unauthorized(self):
        wiki_pages = WikiPage.objects.all()
        self.client.logout()
        self.client.login(username='karol', password='karol1')
        response = self.client.get('/doc/delete/10')
        status_code_for(response).should_be(302)
        wiki_pages_after = WikiPage.objects.all()
        self.assertEqual(len(wiki_pages), len(wiki_pages_after))


    def test_page_in_the_middle_of_toc(self):
        pages_before_deletion = WikiPage.objects.count()
        response = self.client.get('/doc/delete/9')
        status_code_for(response).should_be(302)
        pages_after_deletion = WikiPage.objects.count()
        the(pages_after_deletion).equals(pages_before_deletion - 1)

        child_page = WikiPage.objects.get(pk=10)
        the(child_page.parent).is_none()
        the(child_page.order).is_none()
        the(child_page.is_toc).equals(False)

class NestedSortableTest(FormattedOutputTestCase):
    fixtures = ['nestedSortable.json']

    def setUp(self):
        self.client = Client()
        self.client.login(username='kgebert', password='kgebert1')

    def test_toc_and_other_count(self):
        response = self.client.get('/doc')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['wiki_pages']), 3)

        response = self.client.get('/doc/edit_table_of_contents')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['pages']), 3)
        self.assertEqual(len(response.context['wiki_pages']), 3)

    def test_table_of_contents(self):
        response = self.client.post('/doc/table_of_contents', 
                                    {'list[980]' : 'root', 
                                     'list[998]' : '980',
                                     'list[999]' : '998',
                                     'list[2958]' : '998',
                                     'list[1285]' : '980',
                                     'list[979]' : 'root',
                                     'list[1593]' : 'root',
                                     'list[1239]' : 'root',
                                     'order' : '980,998,999,2958,1285,979,1593,1239'
                                     })
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/doc')
        self.assertEqual(response.status_code, 200)
        added_element = WikiPage.objects.get(pk=1239)
        self.assertEqual(added_element.is_toc, True) # new element in toc has is_toc on True
        self.assertEqual(len(response.context['wiki_pages']), 4) # one element more

    def test_remove_from_toc(self):
        response = self.client.post('/doc/remove_from_table_of_contents', {'list[979]' : 'root', 'list[1593]' : 'root', 'list[1239]' : 'root' })
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/doc')
        self.assertEqual(response.status_code, 200)
        removed_element = WikiPage.objects.get(pk=979)
        self.assertEqual(removed_element.is_toc, False) # new element in Other pages has is_toc on False
        removed_element = WikiPage.objects.get(pk=1593)
        self.assertEqual(removed_element.is_toc, False) # new element in Other pages has is_toc on False
        removed_element = WikiPage.objects.get(pk=1239)
        self.assertEqual(removed_element.is_toc, False) # new element in Other pages has is_toc on False
        self.assertEqual(len(response.context['wiki_pages']), 1) # 3 elements less
