from src.libraries.utility.noseplugins import FormattedOutputTestCase
from django.test.client import Client
import src.mauthor.localization.utils import create_id_string,\
    get_xliff
import src.mauthor.localization.models import Page, Xliff, ContentXML, Field, Module
from src.lorepo.mycontent.models import Content

class BuildXliffDocumentTests(FormattedOutputTestCase):
    fixtures = ['get_data_for_translation.json']
    
    def setUp(self):
        self.client = Client()
        self.module1 = Module("TrueFalse1", 'TrueFalse')
        self.module2 = Module("Connection1", 'Connection')
        self.module3 = Module("crossword1", 'Crossword')
        
        self.module1.fields.append(Field("some weeks ago", "Questions", 'html', "Question", 1))
        self.module2.fields.extend([Field("when I first moved back to ePoland", "Left column", 'html', "content", 0), 
                                    Field("I am superman", "Right column", 'html', "content", 0)])
        self.module3.fields.append(Field("I wrote back an article which had a mixed but mostly negative", "Crossword"))
        
        self.page1 = Page('Page 1', 'random1')
        self.page2 = Page('Page 2', 'random2')
        
        self.page1.modules = [
                        self.module1,
                        self.module2
                      ]
        self.page2.modules = [
                        self.module3
                      ]
        self.TEST_DATA = [
                     self.page1,
                     self.page2
                     ]
        self.xliff = Xliff(get_xliff())

    def tearDown(self):
        pass

    def test_get_xliff_base_elements(self):
        root = self.xliff.document.getElementsByTagName('xliff')
        file_element = self.xliff.document.getElementsByTagName('file')
        body = self.xliff.document.getElementsByTagName('body')
        
        self.assertEqual(1, len(root))
        self.assertEqual(1, len(file_element))
        self.assertEqual(1, len(body))
        
    def test_root_attributes(self):
        root = self.xliff.document.getElementsByTagName('xliff')[0]
        
        self.assertTrue(root.hasAttribute('version'))
        self.assertTrue(root.hasAttribute('xmlns'))
        
    def test_file_attributes(self):
        file_element = self.xliff.document.getElementsByTagName('file')[0]
        
        self.assertTrue(file_element.hasAttribute('source-language'))
        self.assertTrue(file_element.hasAttribute('target-language'))
        self.assertTrue(file_element.hasAttribute('original'))
        self.assertTrue(file_element.hasAttribute('datatype'))
        
    def test_insert_texts_for_translation(self):
        self.xliff.insert_texts_for_translation(self.TEST_DATA, 30)
        
        groups = self.xliff.document.getElementsByTagName('group')
        trans_units = self.xliff.document.getElementsByTagName('trans-unit')
        sources = self.xliff.document.getElementsByTagName('source')
        
        self.assertEqual(2, len(groups))
        self.assertEqual(4, len(trans_units))
        self.assertEqual(4, len(sources))
    
    def test_insert_group(self):
        group = self.xliff.insert_group_element(self.page1)
        groups = self.xliff.document.getElementsByTagName('group')
        
        self.assertEqual(1, len(groups))
        self.assertTrue(group.hasAttribute('id'))
        
    def test_create_id_string(self):
        expected_id_string = 'TrueFalse1:TrueFalse|Questions|html|Question|1'
        id_string = create_id_string(self.module1.fields[0], self.module1)
        
        self.assertEqual(expected_id_string, id_string)
        
    def test_insert_trans_unit(self):
        group = self.xliff.insert_group_element(self.page1)
        trans_unit = self.xliff.insert_trans_unit_element(group, self.module1.fields[0], self.module1)
        trans_units = self.xliff.document.getElementsByTagName('trans-unit')
       
        self.assertEqual(1, len(trans_units))
        self.assertTrue(trans_unit.hasAttribute('id'))
        
    def test_insert_source(self):
        group = self.xliff.insert_group_element(self.page1)
        trans_unit = self.xliff.insert_trans_unit_element(group, self.module1.fields[0], self.module1)
        self.xliff.insert_source(trans_unit, self.module1.fields[0])
        sources = self.xliff.document.getElementsByTagName('source')
        
        self.assertEqual(1, len(sources))
        self.assertEqual('some weeks ago', sources[0].firstChild.data)

    def test_insert_target(self):
        group = self.xliff.insert_group_element(self.page1)
        trans_unit = self.xliff.insert_trans_unit_element(group, self.module1.fields[0], self.module1)
        self.xliff.insert_target(trans_unit, self.module1.fields[0])
        targets = self.xliff.document.getElementsByTagName('target')
        
        self.assertEqual(1, len(targets))
        self.assertTrue(targets[0].hasAttribute('state'))
        self.assertEqual('needs-translation', targets[0].getAttribute('state'))
        self.assertEqual('some weeks ago', targets[0].firstChild.data)
        
class GetDataForTranslationTests(FormattedOutputTestCase):
    fixtures = ['get_data_for_translation.json']
    
    def setUp(self):
        self.client = Client()
        self.content_id = 30
        self.xml_base = ContentXML(self.content_id)
        self.page = Page('Page 1', 'random')
        self.modules = self.xml_base.get_module_elements(self.page)
        
    def tearDown(self):
        pass
    
    def test_get_base_xml(self):
        pages = self.xml_base.document.getElementsByTagName('page')
        
        self.assertEqual(1, len(pages))
        self.assertTrue(pages[0].hasAttribute('href'))
        
    def test_get_pages(self):
        pages = self.xml_base.get_pages()
        
        self.assertEqual(1, len(pages))
        self.assertEqual('Page 1', pages[0].name)
        
    def test_get_page_modules(self):
        self.assertEqual(10, len(self.modules))
        
    def test_get_module_texts_text_module(self):
        text_module = self.xml_base.get_module_element_by_id(self.modules, 'Title')
        module = self.xml_base.get_module(text_module)
        
        self.assertEqual('<div style="text-align: center;">Title</div>', module.fields[0].value)
        self.assertEqual('Title', module.id)
        self.assertEqual('Text', module.fields[0].name)
        self.assertEqual(None, module.fields[0].list_name)
        self.assertEqual(None, module.fields[0].list_index)
        
    def test_get_module_texts_button_module(self):
        button_module = self.xml_base.get_module_element_by_id(self.modules, 'PrevPage')
        module = self.xml_base.get_module(button_module)
        
        self.assertEqual('left', module.fields[0].value)
        self.assertEqual('PrevPage', module.id)
        self.assertEqual('Title', module.fields[0].name)
        self.assertEqual(None, module.fields[0].list_name)
        self.assertEqual(None, module.fields[0].list_index)
    
    def test_get_module_texts_choice_module(self):
        choice_module = self.xml_base.get_module_element_by_id(self.modules, 'Choice1')
        module = self.xml_base.get_module(choice_module)
        
        self.assertEqual(2, len(module.fields))
        
        self.assertEqual('A', module.fields[0].value)
        self.assertEqual('B', module.fields[1].value)
        
        self.assertEqual('Choice1', module.id)
        self.assertEqual('Choice1', module.id)
        
        self.assertEqual('Item', module.fields[0].name)
        self.assertEqual('Item', module.fields[1].name)
        
        self.assertEqual('Text', module.fields[0].list_name)
        self.assertEqual('Text', module.fields[1].list_name)
        
        self.assertEqual(0, module.fields[0].list_index)
        self.assertEqual(1, module.fields[1].list_index)
        
    def test_get_module_texts_ordering_module(self):
        ordering_module = self.xml_base.get_module_element_by_id(self.modules, 'Ordering1')
        module = self.xml_base.get_module(ordering_module)
        
        self.assertEqual(3, len(module.fields))
        
        self.assertEqual('1', module.fields[0].value)
        self.assertEqual('2', module.fields[1].value)
        self.assertEqual('3', module.fields[2].value)
        
        self.assertEqual('Ordering1', module.id)
        self.assertEqual('Ordering1', module.id)
        self.assertEqual('Ordering1', module.id)
        
        self.assertEqual('Item', module.fields[0].name)
        self.assertEqual('Item', module.fields[1].name)
        self.assertEqual('Item', module.fields[2].name)
        
        self.assertEqual('Text', module.fields[0].list_name)
        self.assertEqual('Text', module.fields[1].list_name)
        self.assertEqual('Text', module.fields[2].list_name)
        
        self.assertEqual(0, module.fields[0].list_index)
        self.assertEqual(1, module.fields[1].list_index)
        self.assertEqual(2, module.fields[2].list_index)

    def test_get_module_texts_source_list_module(self):
        source_list_module = self.xml_base.get_module_element_by_id(self.modules, 'Source list1')
        module = self.xml_base.get_module(source_list_module)
        
        self.assertEqual(3, len(module.fields))
        
        self.assertEqual('Item 1', module.fields[0].value)
        self.assertEqual('Item 2', module.fields[1].value)
        self.assertEqual('Item 3', module.fields[2].value)
        
        self.assertEqual('Source list1', module.id)
        
        self.assertEqual('Items-0', module.fields[0].name)
        self.assertEqual('Items-1', module.fields[1].name)
        self.assertEqual('Items-2', module.fields[2].name)
        
    def test_get_module_texts_report_module(self):
        report_module =self.xml_base.get_module_element_by_id(self.modules, 'Report1')
        module = self.xml_base.get_module(report_module)
        
        self.assertEqual(4, len(module.fields))
        
        self.assertEqual('No of errors', module.fields[0].value)
        self.assertEqual('No of checks', module.fields[1].value)
        self.assertEqual('Results:', module.fields[2].value)
        self.assertEqual('Total:', module.fields[3].value)
        
        self.assertEqual('Report1', module.id)
        self.assertEqual('Report1', module.id)
        self.assertEqual('Report1', module.id)
        self.assertEqual('Report1', module.id)
        
        self.assertEqual('ErrorCount', module.fields[0].name)
        self.assertEqual('CheckCount', module.fields[1].name)
        self.assertEqual('Results', module.fields[2].name)
        self.assertEqual('Total', module.fields[3].name)
        
    def test_get_module_texts_addon_module(self):
        addon_module = self.xml_base.get_module_element_by_id(self.modules, 'Connection1')
        module = self.xml_base.get_addon(addon_module, ['content'])
        
        self.assertEqual(4, len(module.fields))
        
        self.assertEqual('Karol<br>', module.fields[0].value)
        self.assertEqual('Michal', module.fields[1].value)
        self.assertEqual('Mateusz<br>', module.fields[2].value)
        self.assertEqual('Lukasz', module.fields[3].value)
        
        self.assertEqual('Connection1', module.id)
        self.assertEqual('Connection1', module.id)
        self.assertEqual('Connection1', module.id)
        self.assertEqual('Connection1', module.id)
        
        self.assertEqual('Left column', module.fields[0].name)
        self.assertEqual('Left column', module.fields[1].name)
        self.assertEqual('Right column', module.fields[2].name)
        self.assertEqual('Right column', module.fields[3].name)
        
        self.assertEqual('content', module.fields[0].list_name)
        self.assertEqual('content', module.fields[1].list_name)
        self.assertEqual('content', module.fields[2].list_name)
        self.assertEqual('content', module.fields[3].list_name)
        
        self.assertEqual(0, module.fields[0].list_index)
        self.assertEqual(1, module.fields[1].list_index)
        self.assertEqual(0, module.fields[2].list_index)
        self.assertEqual(1, module.fields[3].list_index)

class GetPagesForTranslationTests(FormattedOutputTestCase):
    fixtures = ['get_pages_for_translation.json']
    
    def setUp(self):
        self.client = Client()
        self.content_id = 873
        self.xml_base = ContentXML(self.content_id)
        
    def tearDown(self):
        pass

    def test_get_pages_for_translation(self):
        pages = self.xml_base.get_pages_for_translation()

        self.assertEqual(4, len(pages))
        
        self.assertEqual(3, len(pages[0].modules))
        self.assertEqual('', pages[0].folder_name)

        self.assertEqual(3, len(pages[1].modules))
        self.assertEqual('', pages[1].folder_name)
        
        self.assertEqual(3, len(pages[2].modules))
        self.assertEqual('commons/', pages[2].folder_name)
        
        self.assertEqual(3, len(pages[3].modules))
        self.assertEqual('commons/', pages[3].folder_name)
        
    def test_get_pages_and_append_element(self):
        pages = self.xml_base.get_pages()
        
        self.assertEqual(0, len(pages[1].modules))
        
        pages[0].modules.append(Field('a', 'b'))
        pages[1].modules.append(Field('d', 'e'))
        
        self.assertEqual(1, len(pages[1].modules))
        
class MetadataExportTests(FormattedOutputTestCase):
    fixtures = ['metadata_export.json']
    
    def setUp(self):
        self.client = Client()
        self.xliff = Xliff(get_xliff())
        
    def tearDown(self):
        pass
    
    def test_get_metadata_with_data(self):
        content = Content.objects.filter(pk=890)[0]
        metadata = content.get_metadata()
        expected_title = 'test metadata'
        expected_tags = 'test, metadata'
        expected_desc = 'test metadata description'
        expected_short_desc = 'test metadata short description'
        
        self.assertEqual(expected_title, metadata['title'])
        self.assertEqual(expected_tags, metadata['tags'])
        self.assertEqual(expected_desc, metadata['description'])
        self.assertEqual(expected_short_desc, metadata['short_description'])
        
    def test_get_metadata_without_data(self):
        content = Content.objects.filter(pk=899)[0]
        metadata = content.get_metadata()
        expected_title = 'test metadata no metadata'
        
        self.assertEqual(expected_title, metadata['title'])
        self.assertEqual('', metadata['tags'])
        self.assertEqual('', metadata['description'])
        self.assertEqual('', metadata['short_description'])
        
    def test_insert_metadata_with_data_into_xliff(self):
        self.xliff.insert_metadata_element(890)
        metadata_node = self.xliff.get_group_element_by_id('metadata')
        
        self.assertIsNotNone(metadata_node)
        
        source_nodes = metadata_node.getElementsByTagName('source')
        target_nodes = metadata_node.getElementsByTagName('target')
        
        self.assertEqual('group', metadata_node.nodeName)
        self.assertEqual(4, len(metadata_node.childNodes))
        self.assertEqual(4, len(source_nodes))
        self.assertEqual(4, len(target_nodes))
    
    def test_insert_metadata_without_data_into_xliff(self):
        self.xliff.insert_metadata_element(899)
        metadata_node = self.xliff.get_group_element_by_id('metadata')
        
        self.assertIsNotNone(metadata_node)
        
        source_nodes = metadata_node.getElementsByTagName('source')
        target_nodes = metadata_node.getElementsByTagName('target')
        
        self.assertEqual('group', metadata_node.nodeName)
        self.assertEqual(1, len(metadata_node.childNodes))
        self.assertEqual(1, len(source_nodes))
        self.assertEqual(1, len(target_nodes))