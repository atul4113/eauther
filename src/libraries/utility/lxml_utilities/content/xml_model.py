from libraries.utility.lxml_utilities.content.content_xml import NEWEST_CONTENT_XML_VERSION, StyleTuple
from libraries.utility.lxml_utilities.utilities import remove_all_elements_from_xml, ensure_subelement_exists
from lxml import etree


class ContentXML(object):

    def __init__(self, content_xml):
        self.content_root = content_xml
        self._layouts_element = None
        self._styles_element = None

    @classmethod
    def fromstring(cls, content_xml_string):
        return cls(etree.fromstring(content_xml_string))

    @classmethod
    def fromEtree(cls, content_etree):
        return cls(content_etree.getroot())

    def update_content_version(self):
        self.content_root.set("version", NEWEST_CONTENT_XML_VERSION)

    def override_content_xml_with_layouts_and_css(self, semi_responsive_configuration):
        self._prepare_content_tags()

        for layout in list(semi_responsive_configuration.layouts.values()):
            self._create_layout_element(layout)

        for style in list(semi_responsive_configuration.styles.values()):
            self._create_style_element(style)

    def update_content_xml_with_layouts_and_css(self, parsed_content_layouts):
        self._prepare_content_tags()

        for layout in list(parsed_content_layouts.layouts.values()):
            self._create_layout_element(layout)

        for style in list(parsed_content_layouts.styles.values()):
            self._create_style_element(style)

    def _prepare_content_tags(self):
        remove_all_elements_from_xml(self.content_root, "layout")
        remove_all_elements_from_xml(self.content_root, "layouts")
        remove_all_elements_from_xml(self.content_root, "style")
        remove_all_elements_from_xml(self.content_root, "styles")

        self._layouts_element = ensure_subelement_exists(self.content_root, "layouts")
        self._styles_element = ensure_subelement_exists(self.content_root, "styles")

    # noinspection PyMethodMayBeStatic
    def _create_style_element(self, style):
        style_element = etree.SubElement(self._styles_element, "style")
        style_element.set("name", style.name)
        style_element.set("id", style.id)
        if style.is_default is not None and style.is_default:
            style_element.set("isDefault", str(style.is_default).lower())
        style_element.text = style.css

    # noinspection PyMethodMayBeStatic
    def _create_layout_element(self, layout):
        layout_element = etree.SubElement(self._layouts_element, "layout")
        layout_element.set("name", layout.name)
        layout_element.set("id", layout.id)
        if layout.is_default is not None and layout.is_default:
            layout_element.set("isDefault", str(layout.is_default).lower())

        if layout.use_device_orientation:
            device_orientation = etree.SubElement(layout_element, "deviceOrientation")
            device_orientation.set("value", layout.device_orientation)

        style = etree.SubElement(layout_element, "style")
        style.set("id", layout.styleid)
        threshold = etree.SubElement(layout_element, "threshold")
        threshold.set("width", str(layout.threshold))

    def __str__(self):
        return etree.tostring(self.content_root, encoding="utf-8")