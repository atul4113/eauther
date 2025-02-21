from libraries.utility.lxml_utilities.content.content_xml import CONTENT_MAIN_XML_PARSERS, OLD_CONTENT_XML_VERSION
from lxml import etree


def ensure_subelement_exists(root_element, element):
    found_element = root_element.find(element)
    if found_element is None:
        return etree.SubElement(root_element, element)

    return found_element


def parse_main_xml_layouts(main_xml_root):
    version = main_xml_root.get("version", OLD_CONTENT_XML_VERSION)
    return CONTENT_MAIN_XML_PARSERS[version](main_xml_root)


def remove_all_elements_from_xml(root, element):
    for found_element in root.iterfind(".//{0}".format(element)):
        found_element.getparent().remove(found_element)
