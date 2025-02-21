from django.contrib.auth.models import User

from tests_src.TestCase import DBTestCase
from lorepo.filestorage.models import FileStorage
from pytest import fixture
from xml_parsers.explicit_parsers.lesson_copy_parser import LessonCopyParser

from tests_src.path_utils import LoadXMLsFromFiles, LoadFileMixin, GetPathMixin
from tests_src.xml_utils import ETreeXMLDiffMixin


@fixture(scope='function')
def users():
    return {
        'old_owner': User.objects.create(),
        'new_owner': User.objects.create()
    }


@fixture(scope='function')
def database_pages(users):
    return [
        FileStorage.objects.create(pk=5364925476896768, content_type='xml', contents='page1', owner=users['old_owner'], version=1, meta=''),
        FileStorage.objects.create(pk=6176640607191040, content_type='xml', contents='page2', owner=users['old_owner'], version=1, meta=''),
        FileStorage.objects.create(pk=6035369737584640, content_type='xml', contents='page3', owner=users['old_owner'], version=1, meta=''),
        FileStorage.objects.create(pk=6494737159421952, content_type='xml', contents='page4', owner=users['old_owner'], version=1, meta=''),
        FileStorage.objects.create(pk=4243434342342342, content_type='xml', contents='page5', owner=users['old_owner'], version=1, meta='')
    ]


class TestLessonCopyParser(LoadXMLsFromFiles, ETreeXMLDiffMixin, LoadFileMixin, GetPathMixin, DBTestCase):
    INPUT_FILE_PATH_ALL = 'xml_parsers/explicit_parsers/data/lesson_copy_input.xml'
    INPUT_FILE_PATH_REMOVE = 'xml_parsers/explicit_parsers/data/lesson_copy_input_remove.xml'

    def test_parser_correctly_copy_all_pages(self, users, database_pages):
        parser = LessonCopyParser(new_author=users['new_owner'])
        xmls = self.load_xmls(input=self.INPUT_FILE_PATH_ALL)

        input_xml = xmls[1]['input'].getroot()
        parser.parse(self.get_file_object(self.INPUT_FILE_PATH_ALL))

        output_data = parser.get_output_value()
        output_xml = self.load_xml_from_string(output_data)

        pages_count = 0

        for page in output_xml.iter('page'):
            pages_count += 1
            db_page = FileStorage.objects.get(id=page.attrib['href'])
            assert db_page not in database_pages
            assert db_page.owner.username == users['new_owner'].username

        assert 10 == FileStorage.objects.all().count()
        assert 5 == pages_count

        self.assert_are_equals(input_xml, output_xml, ('page', 'href'))

    def test_parser_remove_pages_which_are_not_included_to_extract(self, users, database_pages):
        parser = LessonCopyParser(new_author=users['new_owner'], pages_to_extract=[1])
        xmls = self.load_xmls(input=self.INPUT_FILE_PATH_REMOVE)

        input_xml = xmls[1]['input'].getroot()

        parser.parse(self.get_file_object(self.INPUT_FILE_PATH_ALL))

        output_data = parser.get_output_value()
        output_xml = self.load_xml_from_string(output_data)

        pages_count = 0

        for page in output_xml.iter('page'):
            pages_count += 1
            db_page = FileStorage.objects.get(id=page.attrib['href'])
            assert db_page not in database_pages
            assert db_page.owner.username == users['new_owner'].username

        assert 4 == pages_count
        self.assert_are_equals(input_xml, output_xml, ('page', 'href'))

    def test_parser_are_not_removing_pages_from_chapters(self, users, database_pages):
        parser = LessonCopyParser(new_author=users['new_owner'], pages_to_extract=[2])
        xmls = self.load_xmls(input=self.INPUT_FILE_PATH_ALL)

        input_xml = xmls[1]['input'].getroot()

        parser.parse(self.get_file_object(self.INPUT_FILE_PATH_ALL))

        output_data = parser.get_output_value()
        output_xml = self.load_xml_from_string(output_data)

        pages_count = 0

        for page in output_xml.iter('page'):
            pages_count += 1
            db_page = FileStorage.objects.get(id=page.attrib['href'])
            assert db_page not in database_pages
            assert db_page.owner.username == users['new_owner'].username

        assert 5 == pages_count
        self.assert_are_equals(input_xml, output_xml, ('page', 'href'))

    def test_parser_are_not_removing_pages_from_folder(self, users, database_pages):
        parser = LessonCopyParser(new_author=users['new_owner'], pages_to_extract=[3])
        xmls = self.load_xmls(input=self.INPUT_FILE_PATH_ALL)

        input_xml = xmls[1]['input'].getroot()

        parser.parse(self.get_file_object(self.INPUT_FILE_PATH_ALL))

        output_data = parser.get_output_value()
        output_xml = self.load_xml_from_string(output_data)

        pages_count = 0

        for page in output_xml.iter('page'):
            pages_count += 1
            db_page = FileStorage.objects.get(id=page.attrib['href'])
            assert db_page not in database_pages
            assert db_page.owner.username == users['new_owner'].username

        assert 5 == pages_count
        self.assert_are_equals(input_xml, output_xml, ('page', 'href'))