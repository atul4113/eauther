from libraries.utility.noseplugins import FormattedOutputTestCase
from mauthor.localization.models import Xliff, ContentXML, Page, Field
from mauthor.localization.utils import get_xliff, get_xml_base_for_content, get_content
from mauthor.localization.exceptions import ContentException

class fakeContent(object):
    def __init__(self):
        self.id = None
        self.file = fakeFile()
        
class fakeFile(object):
    def __init__(self):
        self.version = 1

class GetTranslatedDataTests(FormattedOutputTestCase):
    fixtures = ['get_data_for_translation.json']
    
    def setUp(self):
        self.xliff = Xliff(get_xliff('initdata/xliff/test.xlf'))
        self.groups = self.xliff.get_group_elements(lambda x: x.getAttribute('id') != 'metadata|metadata')
        self.content_id = 30
        self.xml = ContentXML(self.content_id)
        self.page = Page('Page 1', 'random')
        self.modules = self.xml.get_module_elements(self.page)

    def tearDown(self):
        pass
    
    def test_get_metadata(self):
        metadata = self.xliff.get_metadata_from_metadata_element()
        
        self.assertEqual('Titre', metadata['title'])
        self.assertEqual('titre, francais', metadata['tags'])
        self.assertEqual('sorte', metadata['description'])
        self.assertEqual('court', metadata['short_description'])
    
    def test_set_content_metadata(self):
        content = get_content(self.content_id)
        metadata = self.xliff.get_metadata_from_metadata_element()
        content.set_metadata(metadata)
        
        self.assertEqual('Titre', content.title)
        self.assertEqual('titre, francais', content.tags)
        self.assertEqual('sorte', content.description)
        self.assertEqual('court', content.short_description)
    
    def test_get_content_id(self):
        content_id = self.xliff.get_content_id()
        
        self.assertEqual(2403, content_id)
    
    def test_get_content_id_raise_no_id_exception(self):
        content = fakeContent()
        self.xliff.set_content_id(content)
        self.assertRaises(ContentException, self.xliff.get_content_id)
        
    def test_get_xml_base_for_content_raise_invalid_id_exception(self):
        self.assertRaises(ContentException, get_xml_base_for_content, '1234567890')
    
    def test_get_href_by_page_name_fill_imporant_information(self):
        self.xml.get_href_by_page_id('random2')
        
        self.assertEqual(1, len(self.xml.errors))
        self.assertTrue('Page with id random2 not found.' in self.xml.errors[0])
        
    def test_get_groups(self):
        self.assertEqual(1, len(self.groups))
        
    def test_get_pages_with_texts(self):
        pages = self.xliff.get_pages_with_modules_and_fields(self.groups)
        
        self.assertEqual(1, len(pages))
        self.assertEqual(4, len(pages[0].modules))
        
        expected_content1 = 'rogue'
        expected_content2 = 'soleil'
        values = [field.value for field in pages[0].modules[1].fields]

        self.assertTrue(expected_content1 in values)
        self.assertTrue(expected_content2 in values)
        
    def test_get_page_by_number(self):
        page = self.xml.get_page_element(0)
        
        self.assertEqual('58', page.getAttribute('href'))
        
    def test_set_texts_for_text_module(self):
        text_module = self.xml.get_module_element_by_id(self.modules, 'Title',)
        field = Field('Karol', '')

        text_module_text_before = text_module.firstChild.firstChild.data
        self.assertEqual('<div style="text-align: center;">Title</div>', text_module_text_before)
        
        self.xml.set_texts_for_text_module(text_module, field)

        text_module_text_after = text_module.firstChild.firstChild.data
        self.assertEqual('Karol', text_module_text_after)
        
    def test_set_texts_for_button_module(self):
        button_module = self.xml.get_module_element_by_id(self.modules, 'PrevPage')
        field = Field('Karol', '')

        button_text_before = button_module.firstChild.getAttribute('text')
        self.assertEqual('left', button_text_before) 

        self.xml.set_texts_for_button_module(button_module, field)

        button_text_after = button_module.firstChild.getAttribute('text')
        self.assertEqual('Karol', button_text_after)

    def test_set_texts_for_choice_module(self):
        choice_module = self.xml.get_module_element_by_id(self.modules, 'Choice1')
        field = Field('Karol', 'Text', 'html', '', 0)

        choice_text_before = choice_module.getElementsByTagName('text')[0].firstChild.data
        self.assertEqual('A', choice_text_before) 

        self.xml.set_texts_for_choice_module(choice_module, field)

        choice_text_after = choice_module.getElementsByTagName('text')[0].firstChild.data
        self.assertEqual('Karol', choice_text_after)
    
    def test_set_texts_for_ordering_module(self):
        ordering_module = self.xml.get_module_element_by_id(self.modules, 'Ordering1')
        field = Field('Karol', 'Text', 'html' ,'', 0)

        ordering_text_before = ordering_module.getElementsByTagName('item')[0].firstChild.data
        self.assertEqual('1', ordering_text_before)

        self.xml.set_texts_for_ordering_module(ordering_module, field)

        ordering_text_after = ordering_module.getElementsByTagName('item')[0].firstChild.data
        self.assertEqual('Karol', ordering_text_after)
    
    def test_set_texts_for_source_list_module(self):
        source_list_module = self.xml.get_module_element_by_id(self.modules, 'Source list1')
        field = Field('Karol', 'Text-0', 'string', '', 0)

        source_list_text_before = source_list_module.getElementsByTagName('item')[0].getAttribute('text')
        self.assertEqual('Item 1', source_list_text_before)

        self.xml.set_texts_for_source_list_module(source_list_module, field)

        source_list_text_after = source_list_module.getElementsByTagName('item')[0].getAttribute('text')
        self.assertEqual('Karol', source_list_text_after)
    
    def test_set_texts_for_report_module(self):
        report_module = self.xml.get_module_element_by_id(self.modules, 'Report1')
        field = Field('Karol', 'ErrorCount')

        report_text_before = report_module.getElementsByTagName('label')[0].getAttribute('value')
        self.assertEqual('No of errors', report_text_before)

        self.xml.set_texts_for_report_module(report_module, field)

        report_text_after = report_module.getElementsByTagName('label')[0].getAttribute('value')
        self.assertEqual('Karol', report_text_after)
    
    def test_set_texts_for_connection_module(self):
        connection_module = self.xml.get_module_element_by_id(self.modules, 'Connection1')
        field = Field('Karol', 'Left column', 'html', 'content', 0)

        connection_text_before = connection_module.getElementsByTagName('items')[0].firstChild.childNodes[1].firstChild.data
        self.assertEqual('Karol<br>', connection_text_before)

        self.xml.set_texts_for_addon_module(connection_module, field)

        connection_text_after = connection_module.getElementsByTagName('items')[0].firstChild.childNodes[1].firstChild.data
        self.assertEqual('Karol', connection_text_after)
    
    def test_set_texts_for_glossary_module(self):
        glossary_module = self.xml.get_module_element_by_id(self.modules, 'Glossary1')
        field = Field('Karol', 'List of words', 'html', 'Text', 0)

        glossary_text_before = glossary_module.getElementsByTagName('item')[0].getElementsByTagName('property')[1].getAttribute('value')
        self.assertEqual('Key', glossary_text_before)

        self.xml.set_texts_for_addon_module(glossary_module, field)

        glossary_text_after = glossary_module.getElementsByTagName('item')[0].getElementsByTagName('property')[1].getAttribute('value')
        self.assertEqual('Karol', glossary_text_after)

    def test_get_module_by_id_with_wrong_id(self):
        glossary_module = self.xml.get_module_element_by_id(self.modules, 'Glossary123')
        
        self.assertEqual(1, len(self.xml.errors))
        self.assertTrue('Glossary123' in self.xml.errors[0])
        self.assertIsNone(glossary_module)