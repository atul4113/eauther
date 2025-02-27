from src.libraries.utility.noseplugins import FormattedOutputTestCase
import src.mauthor.localization.models import XliffXMLNode, ContentXML
from nose.plugins.attrib import attr
from xml.dom import minidom
from src.libraries.utility.test_assertions import the

class StubbedWriter():
    def write(self, data):
        self.data = data

class XliffXMLNodeTests(FormattedOutputTestCase):
    @attr('unit')
    def test_replace_html_chars(self):
        node = XliffXMLNode('<style>\r\n<!--\r\n body { font-family: "Verdana"; } --></style><b>Some&nbsp;text</b>')
        writer = StubbedWriter()
        node.writexml(writer)

        self.assertEqual(writer.data, '<it id="1" pos="open">&lt;style&gt;</it>\n<it id="2" pos="open">&lt;!--\r\n body { font-family: &quot;Verdana&quot;; } --&gt;</it><it id="3" pos="close">&lt;/style&gt;</it><it id="4" pos="open">&lt;b&gt;</it>Some&amp;nbsp;text<it id="5" pos="close">&lt;/b&gt;</it>')

    @attr('unit')
    def test_replace_lower_than_or_equal(self):
        node = XliffXMLNode('<=')
        writer = StubbedWriter()
        node.writexml(writer)

        self.assertEqual(writer.data, '&amp;lt;=')

    @attr('unit')
    def test_replace_when_larger_than_is_between_html_tag(self):
        node = XliffXMLNode('<div>></div>')
        writer = StubbedWriter()
        node.writexml(writer)

        self.assertEqual(writer.data, '<it id="1" pos="open">&lt;div&gt;</it>&amp;gt;<it id="2" pos="close">&lt;/div&gt;</it>')

    @attr('unit')
    def test_replace_when_lower_than_is_between_html_tag(self):
        node = XliffXMLNode('<div><</div>')
        writer = StubbedWriter()
        node.writexml(writer)

        self.assertEqual(writer.data, '<it id="1" pos="open">&lt;div&gt;</it>&amp;lt;<it id="2" pos="close">&lt;/div&gt;</it>')

    @attr('unit')
    def test_replace_with_font_and_img(self):
        node = XliffXMLNode('<div style="text-align: center;"><font size="2">Title</font><img src="/file/serve/12345"/></div>')
        writer = StubbedWriter()
        node.writexml(writer)
        self.assertEqual(writer.data, '<it id="1" pos="open">&lt;div style=&quot;text-align: center;&quot;&gt;</it><it id="2" pos="open">&lt;font size=&quot;2&quot;&gt;</it>Title<it id="3" pos="close">&lt;/font&gt;</it><it id="4" pos="open">&lt;img src=&quot;/file/serve/12345&quot; /&gt;</it><it id="5" pos="close">&lt;/div&gt;</it>')
        
class ContentXMLTests(FormattedOutputTestCase):
    fixtures = ['libraries.testing.mycontent.json', 'libraries.testing.filestorage.json', 'libraries.testing.users.json']
    
    def test_get_addon_with_complex_list(self):
        doc = minidom.parseString(SAMPLE_ADDON_WITH_LIST)
        content_xml = ContentXML(1)
        module = content_xml.get_addon(doc.getElementsByTagName('addonModule')[0], ['Text', 'Description'])
        the(module.fields).length_is(6)
        the(module.fields[0].list_index).equals(0)
        the(module.fields[1].list_index).equals(1)
        the(module.fields[2].list_index).equals(2)
        the(module.fields[3].list_index).equals(0)
        the(module.fields[4].list_index).equals(1)
        the(module.fields[5].list_index).equals(2)

    def test_get_addon_with_simple_list(self):
        doc = minidom.parseString(SAMPLE_ADDON_WITH_SIMPLE_LIST)
        content_xml = ContentXML(1)
        module = content_xml.get_addon(doc.getElementsByTagName('addonModule')[0], ['Text', 'Description'])
        the(module.fields).length_is(3)
        the(module.fields[0].list_index).equals(0)
        the(module.fields[1].list_index).equals(1)
        the(module.fields[2].list_index).equals(2)
        
    def test_get_addon_with_one_item_list(self):
        doc = minidom.parseString(SAMPLE_ADDON_WITH_ONE_ITEM_LIST)
        content_xml = ContentXML(1)
        module = content_xml.get_addon(doc.getElementsByTagName('addonModule')[0], ['Text', 'Description'])
        the(module.fields).length_is(2)
        the(module.fields[0].list_index).equals(0)
        the(module.fields[1].list_index).equals(0)
        
        
SAMPLE_ADDON_WITH_LIST = """<addonModule addonId="Glossary" id="Glossary1" left="19" top="308" width="89" height="73" right="0" bottom="0" isVisible="true" isLocked="false">
<properties>
<property name="List of words" displayName="" type="list">
<items>
<item>
<property name="ID" displayName="" type="string" value="one"/>
<property name="Text" displayName="" type="string" value="O N E"/>
<property name="Description" displayName="" type="html">
<![CDATA[ Jeden ]]>
</property>
</item>
<item>
<property name="ID" displayName="" type="string" value="two"/>
<property name="Text" displayName="" type="string" value="TWO"/>
<property name="Description" displayName="" type="html">
<![CDATA[ dwa ]]>
</property>
</item>
<item>
<property name="ID" displayName="" type="string" value="three"/>
<property name="Text" displayName="" type="string" value="T H R EEEEEE"/>
<property name="Description" displayName="" type="html">
<![CDATA[ trzy ]]>
</property>
</item>
</items>
</property>
</properties>
</addonModule>"""

SAMPLE_ADDON_WITH_SIMPLE_LIST = """<addonModule addonId="Glossary" id="Glossary1" left="19" top="308" width="89" height="73" right="0" bottom="0" isVisible="true" isLocked="false">
<properties>
<property name="List of words" displayName="" type="list">
<items>
<item>
<property name="Text" displayName="" type="string" value="O N E"/>
</item>
<item>
<property name="Text" displayName="" type="string" value="TWO"/>
</item>
<item>
<property name="Text" displayName="" type="string" value="T H R EEEEEE"/>
</item>
</items>
</property>
</properties>
</addonModule>"""

SAMPLE_ADDON_WITH_ONE_ITEM_LIST = """<addonModule addonId="Glossary" id="Glossary1" left="19" top="308" width="89" height="73" right="0" bottom="0" isVisible="true" isLocked="false">
<properties>
<property name="List of words" displayName="" type="list">
<items>
<item>
<property name="Text" displayName="" type="string" value="O N E"/>
<property name="Description" displayName="" type="string" value="TWO"/>
</item>
</items>
</property>
</properties>
</addonModule>"""