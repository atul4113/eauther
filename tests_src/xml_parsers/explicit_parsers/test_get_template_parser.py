from xml_parsers.explicit_parsers.get_template_parser import GetTemplateParser

from tests_src.path_utils import LoadFileMixin, GetPathMixin


class TestGetTemplateParser(LoadFileMixin, GetPathMixin):
    INPUT_FILE_PATH = 'xml_parsers/explicit_parsers/data/get_pages_list_input.xml'

    def test_get_template(self):
        parser = GetTemplateParser()

        parser.parse(self.get_file_object(self.INPUT_FILE_PATH))

        assert '/file/5950045' == parser.get_entry_attr()