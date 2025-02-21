import os
import StringIO
from lxml import etree
from xml_parsers.EchoXMLGenerator import EchoXMLGenerator


current_dir = os.path.dirname(__file__)


class TestSaxParsing(object):
    SIMPLE_XML_PATH = os.path.join(current_dir, "testdata/simple.xml")

    def test_sox_parser_returns_the_same_xml(self):
        received_data = StringIO.StringIO('')
        with open(self.SIMPLE_XML_PATH, 'r') as source:
            sax_handler = EchoXMLGenerator(out=received_data, encoding='utf-8')
            sax_handler.parse(source)

            parser = etree.XMLParser(strip_cdata=False, resolve_entities=False)
            parsed_xml = etree.tostring(etree.XML(received_data.getvalue(), parser=parser), pretty_print=True)

            with open(self.SIMPLE_XML_PATH, 'r') as input:
                original_xml = etree.tostring(etree.XML(input.read(), parser=parser), pretty_print=True)

            assert parsed_xml == original_xml
