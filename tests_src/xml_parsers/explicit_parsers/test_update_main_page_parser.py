from xml_parsers.explicit_parsers.update_main_page_parser import UpdateMainPageParser

from tests_src.path_utils import LoadFileMixin, GetPathMixin, LoadXMLsFromFiles
from tests_src.xml_utils import ETreeXMLDiffMixin


class TestUpdateMainPageParser(LoadXMLsFromFiles, ETreeXMLDiffMixin, LoadFileMixin, GetPathMixin):
    INPUT_PATH = 'xml_parsers/explicit_parsers/data/update_main_page_input.xml'
    EXPECTED_OUTPUT_PATH = 'xml_parsers/explicit_parsers/data/update_main_page_expected.xml'

    def test_page_urls_are_correctly_changed(self):
        map = {
            "5364925476896768": "3241412341242132",
            "4243434342342342": "1234235425213423",
            "6176640607191040": "5463435342232134",
            "6035369737584640": "6436235345325324",
            "6494737159421952": "2143213412342142",
            "1312312312321332": "1231231231236543"
        }

        parser = UpdateMainPageParser(map)
        parser.parse(self.get_file_object(self.INPUT_PATH))

        expected = self.load_xmls(expected=self.EXPECTED_OUTPUT_PATH)[1]['expected'].getroot()
        output = self.load_xml_from_string(parser.get_output_value())

        self.assert_are_equals(expected, output)



    def test_parser_is_correctly_count_changes_count(self):
        map = {
            "5364925476896768": "3241412341242132",
            "4243434342342342": "1234235425213423",
            "6176640607191040": "5463435342232134",
            "6035369737584640": "6436235345325324",
            "6494737159421952": "2143213412342142",
            "4242342342342342": "4313123123123121",
            "2314234234234232": "2431241212312213"
        }

        parser = UpdateMainPageParser(map)
        parser.parse(self.get_file_object(self.INPUT_PATH))

        assert 5 == parser.get_changes_count()
