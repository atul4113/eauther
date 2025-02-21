from xml_parsers.explicit_parsers.add_titile_to_lesson_parser import AddTitleToXMLParser

from tests_src.path_utils import LoadXMLsFromFiles, GetPathMixin, LoadFileMixin
from tests_src.xml_utils import ETreeXMLDiffMixin


class TestAddTitleToLessonParser(LoadXMLsFromFiles, ETreeXMLDiffMixin, LoadFileMixin, GetPathMixin):
    INPUT_PATH = 'xml_parsers/explicit_parsers/data/add_title_input.xml'
    EXPECTED_PATH = 'xml_parsers/explicit_parsers/data/add_title_expected.xml'

    def test_add_title_to_xml_parser_adds_new_attribute(self):
        xmls = self.load_xmls(expected=self.EXPECTED_PATH)
        parser = AddTitleToXMLParser(title="Sampling Techniques")

        parser.parse(self.get_file_object(self.INPUT_PATH))
        result_xml = self.load_xml_from_string(parser.get_output_value())
        self.assert_are_equals(xmls[1]['expected'].getroot(), result_xml)
