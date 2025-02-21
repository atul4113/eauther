from deepdiff import DeepDiff
from libraries.utility.lxml_utilities.content.content_xml import StyleTuple, LayoutTuple, ParsedSemiResponsiveContent
from libraries.utility.lxml_utilities.content.xml_model import ContentXML

from tests_src.path_utils import GetPathMixin, LoadXMLsFromFiles
from tests_src.xml_utils import etree_to_dict


class TestContentXMLCreation(GetPathMixin, LoadXMLsFromFiles):
    styles = {
        "default": StyleTuple(id="default", name="default", is_default=True, css="style-string-default"),
        "320": StyleTuple(id="320", name="320", is_default=False, css="style-string-320"),
        "TT": StyleTuple(id="TT", name="TT", is_default=False, css="style-string-TT"),
        "desktop": StyleTuple(id="desktop", name="desktop", is_default=False, css="style-string-desktop"),
    }

    layouts = {
        "default": LayoutTuple.horizontal_device(threshold=1000, styleid="default", id="default", name="default", is_default=True),
        "320": LayoutTuple.vertical_device(threshold=320, styleid="320", id="320", name="320", is_default=False),
        "TT": LayoutTuple.no_device(threshold=444, name="TT", id="TT", styleid="TT", is_default=False),
        "desktop": LayoutTuple.no_device(threshold=555, name="desktop", id="desktop", styleid="desktop", is_default=False),
    }

    def __get_parsed_xml(self, content_path, result_path):
        (content, expected_result), _ = self.load_xmls(("content_xml", content_path,), ("content_xml", result_path,))

        contentXML = ContentXML.fromEtree(content)
        contentXML.update_content_version()
        contentXML.override_content_xml_with_layouts_and_css(ParsedSemiResponsiveContent(self.layouts, self.styles))
        return etree_to_dict(contentXML.content_root), etree_to_dict(expected_result.getroot())

    def test_content_v0_to_newest_content(self):
        result, expected_result = self.__get_parsed_xml("content_v0.xml", "result.xml")

        assert DeepDiff(expected_result, result, ignore_order=True) == {}

    def test_content_v2_to_newest_content(self):
        result, expected_result = self.__get_parsed_xml("content_v2.xml", "result.xml")

        assert DeepDiff(expected_result, result, ignore_order=True) == {}
