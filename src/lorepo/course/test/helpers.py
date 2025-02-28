from src import settings
from src.libraries.utility.noseplugins import FormattedOutputTestCase
from src.lorepo.course.helpers import parse_serialized_toc, get_or_create_node,\
    create_chapter_node, get_element_by_id, get_structure_chapters,\
    get_child_element_by, remove_unrelated_resources
from xml.dom import minidom
import re
from nose.plugins.attrib import attr

class CourseHelpersTests(FormattedOutputTestCase):
    def setUp(self):
        self.test_xml = '''
        <course name="Course 1">
            <chapters>
                <chapter chapter-id="1" name="Chapter 1"/>
                <chapter chapter-id="2" name="Chapter 2"/>
                <chapter chapter-id="3" name="Chapter 3"/>
                <chapter chapter-id="4" name="Chapter 4">
                    <chapter chapter-id="5" name="Chapter 4.1">
                        <chapter chapter-id="6" name="Chapter 4.1.1"/>
                    </chapter>
                    <chapter chapter-id="7" name="Chapter 4.2"/>
                </chapter>
            </chapters>
        </course>
        '''

        self.test_xml_resources = '''
        <ebooks>
            <ebook ebook-id="5345825534246912" name="Lesson 7" version="16">
                <resources>
                    <resource page="0" resource-id="6401356696911872"/>
                    <resource page="0" resource-id="5910974510923776"/>
                    <resource page="0" resource-id="6614661952700416"/>
                </resources>
            </ebook>
            <ebook ebook-id="5207287069147136" name="Lesson 2" version="5">
                <resources>
                    <resource page="0" resource-id="5910974510923776"/>
                </resources>
            </ebook>
        </ebooks>
        '''

        self.test_unrelated_resources = '<?xml version="1.0" encoding="utf-8"?><course id="5171003185430528" name="Tests">' \
        '<chapters><chapter chapter-id="1" name="Rozdzial"><lessons><lesson lesson-id="6015428115562496" name="Lesson1" url="http://www.mauthor.com/file/serve/6470969526845440" version="5"/></lessons></chapter></chapters>' \
        '<ebooks>' \
            '<ebook ebook-id="6437640580628480" name="Ebook1" url="http://www.mauthor.com/file/serve/5626544596713472" version="3">' \
                '<resources>' \
                    '<resource page="0" resource-id="6015428115562496"/>' \
                    '<resource page="0" resource-id="123456"/>' \
                '</resources>' \
            '</ebook>' \
            '<ebook ebook-id="123" name="Ebook2" url="http://www.mauthor.com/file/serve/5626544596713472" version="3">' \
                '<resources>' \
                    '<resource page="0" resource-id="6015428115562496"/>' \
                    '<resource page="1" resource-id="123456"/>' \
                '</resources>' \
            '</ebook>' \
        '</ebooks>' \
        '</course>'

    @attr('unit')
    def test_parse_serialized_toc(self):
        input_string = 'Chapter 1[1]=root&Chapter 2[2]=root&Chapter 3[3]=root&Chapter 4[4]=root&Chapter 4.1[5]=4&Chapter 4.1.1[6]=5&Chapter 4.2[7]=4'
        results = parse_serialized_toc(input_string)
        expected_count = 7
        expected_one = {
                        'id' : '1',
                        'parent' : 'root', 
                        'name' : 'Chapter 1'
                        }
        expected_two = {
                        'id' : '6',
                        'parent' : '5',
                        'name' : 'Chapter 4.1.1'
                        }

        self.assertEqual(len(results), expected_count)
        self.assertEqual(results[0], expected_one)
        self.assertEqual(results[5], expected_two)

    @attr('unit')
    def test_get_or_create_node(self):
        parsed_xml = minidom.parseString(self.test_xml)
        node, created = get_or_create_node(parsed_xml, 'course')

        self.assertFalse(created)
        self.assertEqual('course', node.nodeName)

    @attr('unit')
    def test_create_chapter_node(self):
        parsed_xml = minidom.parseString(self.test_xml)
        chapter = {
                'id' : '8',
                'parent' : '1', 
                'name' : 'Chapter 1.1'
                }
        lessons = [{
                'id' : '123123',
                'name' : 'Test Lesson'
                }]
        create_chapter_node(parsed_xml, chapter, lessons)

        chapters_nodes = parsed_xml.getElementsByTagName('chapter')
        newly_created_chapter_node = None
        for chapter_node in chapters_nodes:
            if chapter_node.getAttribute('chapter-id') == '8':
                newly_created_chapter_node = chapter_node

        self.assertIsNotNone(newly_created_chapter_node)
        self.assertEqual('Chapter 1.1', newly_created_chapter_node.getAttribute('name'))
        self.assertEqual('1', newly_created_chapter_node.parentNode.getAttribute('chapter-id'))

    @attr('unit')
    def test_get_element_by_id(self):
        parsed_xml = minidom.parseString(self.test_xml)

        node = get_element_by_id(parsed_xml, 'chapter', '1')

        self.assertEqual('chapter', node.nodeName)
        self.assertEqual('1', node.getAttribute('chapter-id'))

    @attr('unit')
    def test_get_element_by_id_for_non_exisiting_id(self):
        parsed_xml = minidom.parseString(self.test_xml)

        node = get_element_by_id(parsed_xml, 'chapter', '12')

        self.assertIsNone(node)

    @attr('unit')
    def test_get_structure_chapters(self):
        parsed_xml = minidom.parseString(self.test_xml)
        expected_one = {
            'node_id' : '1',
            'name' : 'Chapter 1',
            'kids' : [],
            'lessons' : []
        }
        structure_chapters = get_structure_chapters(parsed_xml)

        self.assertEqual(4, len(structure_chapters))
        self.assertEqual(expected_one, structure_chapters[0])
        self.assertEqual(2, len(structure_chapters[3]['kids']))

    @attr('unit')
    def test_get_resources_child_element_by(self):
        parsed_xml = minidom.parseString(re.sub(r'[\n\t\r][ ]{2,}', '', self.test_xml_resources))
        resources_node = parsed_xml.getElementsByTagName('resources')[0]

        child = get_child_element_by(resources_node, { 'page' : '0', 'resource-id' : '6401356696911872' })
        self.assertEqual('6401356696911872', child.getAttribute('resource-id'))
        self.assertEqual(child.getAttribute('page'), '0')

    @attr('unit')
    def test_get_ebooks_child_element_by(self):
        parsed_xml = minidom.parseString(re.sub(r'[\n\t\r][ ]{2,}', '', self.test_xml_resources))
        ebooks_node = parsed_xml.getElementsByTagName('ebooks')[0]

        child = get_child_element_by(ebooks_node, { 'page' : '0', 'resource-id' : '6401356696911872' })
        self.assertEqual('6401356696911872', child.getAttribute('resource-id'))
        self.assertEqual(child.getAttribute('page'), '0')

    @attr('unit')
    def test_course_with_unrelated_resources(self):
        xml = remove_unrelated_resources(self.test_unrelated_resources)
        self.assertRegex(self.test_unrelated_resources,'resource-id="123456"')
        self.assertNotRegexpMatches(xml,'123456')