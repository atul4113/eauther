from deepdiff import DeepDiff
from lxml import etree

from libraries.utility.lxml_utilities.content.content_xml import CONTENT_MAIN_XML_PARSERS, StyleTuple, LayoutTuple

from tests_src.path_utils import GetPathMixin


class TestSyncingLayoutsToOneToOneRelation(GetPathMixin):
    content_v1_c1_parser_styles = {
        "default": StyleTuple(id="default", name="default", is_default=True, css="default-string-style"),
        "320": StyleTuple(id="320", name="320", is_default=False, css="320-string-style"),
        "TT": StyleTuple(id="TT", name="TT", is_default=False, css="320-string-style"),
        "T2": StyleTuple(id="T2", name="T2", is_default=False, css="T2-string-style")
    }

    content_v1_c1_parser_layouts = {
        "default": LayoutTuple.horizontal_device(threshold=1000, styleid="default", id="default", name="default", is_default=True),
        "320": LayoutTuple.vertical_device(threshold=320, styleid="320", id="320", name="320", is_default=False),
        "TT": LayoutTuple.no_device(threshold=11, name="TT", id="TT", styleid="TT", is_default=False),
        "T2": LayoutTuple.no_device(threshold=22, styleid="T2", name="T2", id="T2", is_default=False)
    }

    content_v1_parser_styles = {
        "default": StyleTuple(id="default", name="default", is_default=True, css="style-string-default"),
        "320": StyleTuple(id="320", name="320", css="style-string-320", is_default=False)
    }

    content_v1_parser_layouts = {
        "default": LayoutTuple.horizontal_device(id="default", name="default", styleid="default", is_default=True, threshold=1000),
        "320": LayoutTuple.vertical_device(id="320", name="320", styleid="320", is_default=False, threshold=320)
    }


    def test_syncing_existing_v1_have_to_create_one_to_one_relation_of_layout_and_css_style(self):
        parsed_xml_layouts = CONTENT_MAIN_XML_PARSERS["2"](etree.parse(self.get_path("contentv1_parsing", "testdata", "contentV1Parser.xml")))

        assert DeepDiff(self.content_v1_parser_styles, parsed_xml_layouts.styles, ignore_order=True) == {}
        assert DeepDiff(self.content_v1_parser_layouts, parsed_xml_layouts.layouts, ignore_order=True) == {}

    def test_syncing_layouts_who_use_the_same_css_style_have_to_create_separate_copies_for_them_and_remove_additional(self):
        parsed_xml_layouts = CONTENT_MAIN_XML_PARSERS["2"](etree.parse(self.get_path("contentv1_parsing", "testdata", "contentV1Parser_c1.xml")))

        assert DeepDiff(self.content_v1_c1_parser_styles, parsed_xml_layouts.styles, ignore_order=True) == {}
        assert DeepDiff(self.content_v1_c1_parser_layouts, parsed_xml_layouts.layouts, ignore_order=True) == {}