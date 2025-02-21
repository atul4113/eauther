from lorepo.filestorage.models import FileStorage
from lorepo.filestorage.utils import create_new_version, create_new_subpages,\
    update_main_page
from django.contrib.auth.models import User
import xml.dom.minidom as minidom
from libraries.utility.noseplugins import FormattedOutputTestCase
from nose.plugins.attrib import attr
from django.http import HttpRequest, HttpResponse
from lorepo.filestorage.views import serve_file
from libraries.utility.test_assertions import the
from libraries.utility.test_stubs import StubReader

class UtilsTests(FormattedOutputTestCase):
    fixtures = ['filestorage.json']

    # TODO fix test
    def _create_new_version(self):
        file_storage = FileStorage.objects.get(pk=1199)
        new_owner = User.objects.get(pk=202)
        new_file_storage = create_new_version(file_storage, new_owner)

        self.assertEqual(file_storage.content_type, new_file_storage.content_type)
        self.assertEqual(new_owner, new_file_storage.owner)
        # The highest version + 1
        self.assertEqual(4, new_file_storage.version)
        self.assertEqual(file_storage.history_for, new_file_storage.history_for)

        self.assertNotEqual(file_storage.contents, new_file_storage.contents)

    # TODO fix test
    def _create_new_version_addon(self):
        # TODO improve this test to actually operate on addon, not just a FileStorage
        file_storage = FileStorage.objects.get(pk=1199)
        new_owner = User.objects.get(pk=202)
        new_file_storage = create_new_version(file_storage, new_owner, is_addon=True)

        self.assertEqual(file_storage.content_type, new_file_storage.content_type)
        self.assertEqual(new_owner, new_file_storage.owner)
        # The highest version + 1
        self.assertEqual(4, new_file_storage.version)
        self.assertEqual(file_storage.history_for, new_file_storage.history_for)

    # TODO fix test
    def _create_new_subpages(self):
        file_storage = FileStorage.objects.get(pk=1199)
        id_mapping = create_new_subpages(file_storage)
        self.assertIn("1198", id_mapping)
        self.assertIn("1202", id_mapping)
        for new_id in list(id_mapping.values()):
            fs = FileStorage.objects.get(pk=new_id)
            self.assertIsNotNone(fs)

    # TODO fix test
    def _update_main_page(self):
        file_storage = FileStorage.objects.get(pk=1199)
        id_mapping = create_new_subpages(file_storage)
        update_main_page(file_storage, id_mapping)
        update_file_storage = FileStorage.objects.get(pk=1199)

        expected_content = "<?xml version='1.0' encoding='UTF-8' ?><interactiveContent><metadata></metadata><libs></libs><pages><page name='page 1' href='%(first_page)s'/><page name='new page' href='%(second_page)s'/></pages><assets></assets></interactiveContent>"
        expected_content = expected_content % {'first_page' : list(id_mapping.values())[0], 'second_page' : list(id_mapping.values())[1]}

        updated_dom = minidom.parseString(update_file_storage.contents)
        expected_dom = minidom.parseString(expected_content)
        self.assertEqual(updated_dom.toxml("utf-8"), expected_dom.toxml("utf-8"))
