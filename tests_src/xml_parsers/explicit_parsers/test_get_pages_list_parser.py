from xml_parsers.explicit_parsers.get_pages_list_parser import GetPagesListParser

from tests_src.path_utils import LoadFileMixin, GetPathMixin


class TestGetPagesList(LoadFileMixin, GetPathMixin):
    INPUT_FILE_PATH = 'xml_parsers/explicit_parsers/data/get_pages_list_input.xml'


    def test_get_pages_list_returns_all_pages(self):
        parser = GetPagesListParser()

        input_file = self.get_file_object(self.INPUT_FILE_PATH)

        parser.parse(input_file)

        assert parser.get_pages_list() == ['5364925476896768', '4243434342342342', '6176640607191040', '6035369737584640', '6494737159421952']