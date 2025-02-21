from django.test.client import Client
from libraries.utility.noseplugins import FormattedOutputTestCase
from xml.dom import minidom
from lorepo.filestorage.models import FileStorage
from libraries.utility.test_assertions import status_code_for, the
from lorepo.mycontent.models import Content

class ViewsTests(FormattedOutputTestCase):
    fixtures = ['update_assets.json']

    def setUp(self):
        super(ViewsTests, self).setUp()
        self.client = Client()
        self.client.login(username='admin', password='admin')

    def tearDown(self):
        super(ViewsTests, self).tearDown()
        self.client.logout()

    def test_new_version_is_recorded(self):
        content_before = Content.objects.get(pk=19)
        versions_before = content_before.filestorage_set.count()
        response = self.client.get('/mycontent/update_assets_async/19/1')
        status_code_for(response).should_be(200)
        content_after = Content.objects.get(pk=19)
        versions_after = content_after.filestorage_set.count()
        the(versions_after).equals(versions_before + 1)

    def test_stop_when_lesson_is_in_edit_mode(self):
        self.client.get('/mycontent/19/editor')
        response = self.client.get('/mycontent/update_assets/19')
        status_code_for(response).should_be(200)

    def test_assets_are_updated(self):
        file_contents_before = FileStorage.objects.get(pk=18).contents
        file_dom_before = minidom.parseString(file_contents_before)
        assets_before = file_dom_before.getElementsByTagName('asset')
        the(assets_before).length_is(1)
        response = self.client.get('/mycontent/update_assets_async/19/1')
        status_code_for(response).should_be(200)
        content_after = Content.objects.get(pk=19)
        file_contents_after = content_after.file.contents
        file_dom_after = minidom.parseString(file_contents_after)
        assets_after = file_dom_after.getElementsByTagName('asset')
        the(assets_after).length_is(4)

    def test_assets_are_not_doubled(self):
        self.client.get('/mycontent/update_assets_async/19/1')
        content_after = Content.objects.get(pk=19)
        file_contents_after = content_after.file.contents
        file_dom_after = minidom.parseString(file_contents_after)
        assets_after = file_dom_after.getElementsByTagName('asset')
        the(assets_after).length_is(4)

        self.client.get('/mycontent/update_assets_async/19/1')
        content_after = Content.objects.get(pk=19)
        file_contents_after = content_after.file.contents
        file_dom_after = minidom.parseString(file_contents_after)
        assets_after = file_dom_after.getElementsByTagName('asset')
        the(assets_after).length_is(4)