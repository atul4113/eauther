from src.libraries.utility.noseplugins import FormattedOutputTestCase
from src.lorepo.mycontent.models import Content
from src.lorepo.exchange.utils import render_manifest
from src.libraries.utility.test_assertions import the
from xml.dom.minidom import parseString
import re
from src.lorepo.exchange.views import _update_resource_urls_to_locals
from nose.plugins.attrib import attr

class ManifestTests(FormattedOutputTestCase):
    fixtures = ['exchange2.json']

    def test_render_manifest(self):
        content = Content.objects.get(pk=34)
        content.passing_score = 76.5
        rendered = render_manifest(content)
        doc = parseString(rendered)
        for min_normalized_measure in doc.getElementsByTagName('imsss:minNormalizedMeasure'):
            the(min_normalized_measure.firstChild.nodeValue).equals('0.765')

class URLCleanUp(FormattedOutputTestCase):
    
    def setUp(self):
        self.pattern = '(http:\/\/www\.(mauthor|minstructor)\.com)?\/file\/serve\/%(id)s' % { 'id' : 123 }

    @attr('unit')
    def test_regex_finds_all(self):

        text_one = 'http://www.mauthor.com/file/serve/123'
        text_two = '/file/serve/123'
        text_three = 'http://www.minstructor.com/file/serve/123'

        matches = re.findall(self.pattern, text_one)
        self.assertEqual(1, len(matches))

        matches = re.findall(self.pattern, text_two)
        self.assertEqual(1, len(matches))

        matches = re.findall(self.pattern, text_three)
        self.assertEqual(1, len(matches))

    @attr('unit')
    def test_update_resource_urls_to_locals(self):
        contents = '''
        <item>
            <property name='Row' type='string' value='2'/>
            <property name='Column' type='string' value='4'/>
            <property name='Content' type='html'>
                <![CDATA[<font color="white"><img src="http://www.mauthor.com/file/serve/123" height="27" width="20"></font>]]></property>
        </item>
        <item>
            <property name='Row' type='string' value='2'/>
            <property name='Column' type='string' value='5'/>
            <property name='Content' type='html'>
                <![CDATA[<font color="white"><img src="http://www.mauthor.com/file/serve/123" height="27" width="20"></font>]]></property>
        </item>
        '''

        local_urls = {
            123 : '3072.jpg'
        }

        expected_contents = '''
        <item>
            <property name='Row' type='string' value='2'/>
            <property name='Column' type='string' value='4'/>
            <property name='Content' type='html'>
                <![CDATA[<font color="white"><img src="../resources/3072.jpg" height="27" width="20"></font>]]></property>
        </item>
        <item>
            <property name='Row' type='string' value='2'/>
            <property name='Column' type='string' value='5'/>
            <property name='Content' type='html'>
                <![CDATA[<font color="white"><img src="../resources/3072.jpg" height="27" width="20"></font>]]></property>
        </item>
        '''

        updated_contents = _update_resource_urls_to_locals(contents, local_urls)

        self.assertEqual(expected_contents, updated_contents)