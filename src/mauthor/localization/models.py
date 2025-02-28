import re
from xml.dom import minidom
from xml.dom.minidom import Childless, Node
from xml.sax.saxutils import escape

from src.mauthor.localization.utils import create_id_string,\
    get_xml_base_for_content, get_file, is_empty, get_properties_for_translation,\
    get_content_from_property, parent_is_list, get_parent, calculate_counter,\
    resolve_id_string,\
    handle_execution,\
    is_list_type, get_list_properties, get_list_properties_by_name,\
    get_property_by_name, make_page_copy, get_content, set_or_create_text_node,\
    generate_id
from src.mauthor.localization.exceptions import NodeNotFoundException, ContentException,\
    NoModulesFoundException, ContentTooBigException
from src.mauthor.localization.utils import get_xliff

from .IcplayerZipped import IcplayerZipped

_moduleTypes = [
    'textModule',
    'buttonModule',
    'choiceModule',
    'orderingModule',
    'sourceListModule',
    'reportModule',
    'addonModule'
]

FILE_SIZE_LIMIT = 1024 * 1024

class ContentXML(object):
    def __init__(self, content_id):
        self.document = get_xml_base_for_content(content_id)
        self.content_id = content_id
        self.errors = []

    def make_xliff_object(self):
        pages = self.get_pages_for_translation()
        xliff = Xliff(get_xliff())
        xliff.insert_texts_for_translation(pages, self.content_id)
        xliff.insert_metadata_element(self.content_id)
        return xliff

    def print_document(self):
        return self.document.toxml(encoding='UTF-8')
    
    def get_pages_for_translation(self):
        pages = self.get_pages()
        addons_fields = self.get_addons_fields_for_translation()
        for page in pages:
            modules_elements = self.get_module_elements(page)
            for module_element in modules_elements:
                module_type = module_element.nodeName
                if module_type == 'addonModule':
                    addon_name = module_element.getAttribute('addonId')
                    addon_fields = addons_fields[addon_name]
                    module = self.get_addon(module_element, addon_fields)
                    module.name = addon_name
                    if len(module.fields) > 0:
                        page.modules.append(module)
                else:
                    module = self.get_module(module_element)
                    if len(module.fields) > 0:
                        page.modules.append(module)
        return pages

    def get_pages(self):
        page_elements = self.get_page_elements()
        pages = []
        for page_element in page_elements:
            name = page_element.getAttribute('name')
            page_element_id_attr = page_element.getAttribute('id')
            if  page_element_id_attr != 'null' and page_element_id_attr != '':
                page_id = page_element_id_attr
            else:
                page_id = generate_id()
                self.set_page_element_id(page_element, page_id)
                
            folder_name = ''
            parent_node = page_element.parentNode
            if parent_node.nodeName == 'folder':
                folder_name = parent_node.getAttribute('name') + '/'

            pages.append(Page(name=name, page_id=page_id, folder_name=folder_name))
        
        content = get_content(self.content_id)
        content.file.contents = self.print_document()
        content.file.save()
        return pages
    
    def set_page_element_id(self, page_element, page_id):
        page_element.setAttribute('id', page_id)
    
    def get_page_elements(self):
        return self.document.getElementsByTagName('page')
    
    def get_page_element(self, number):
        return self.get_page_elements()[number]
    
    def get_page_element_by_id(self, page_id):
        for page_element in self.get_page_elements():
            if page_element.getAttribute('id') == page_id:
                return page_element
    
    def get_href_by_page_id(self, page_id):
        for page_element in self.get_page_elements():
            if page_element.getAttribute('id') == page_id:
                return page_element.getAttribute('href')
        info = 'Page with id ' + page_id + ' not found.'
        self.errors.append(info)
    
    def get_module_element_by_id(self, modules, module_id):
        if len(modules) == 0:
            raise NoModulesFoundException()
        for module in modules:
            if module.nodeType == 3:
                return None
            if module.hasAttribute('id') and module.getAttribute('id') == module_id:
                return module
        info = 'Module with id ' + module_id + ' not found.'
        self.errors.append(info)
    
    def set_translated_texts(self, pages, user):
        for page in pages:
            href = self.get_href_by_page_id(page.id)
            if href:
                page_file = make_page_copy(href, user)
                page_xml = minidom.parseString(page_file.contents)
                module_nodes = page_xml.getElementsByTagName('modules')
                modules = module_nodes[0].childNodes if len(module_nodes) > 0 else []
                for module in page.modules:
                    module_element = self.get_module_element_by_id(modules, module.id)
                    if module_element:
                        for field in module.fields:
                            self.set_module_translated_content(module_element, field)
                page_file.contents = page_xml.toxml('UTF-8')
                page_file.save()
                page_element = self.get_page_element_by_id(page.id)
                page_element.setAttribute('href', str(page_file.pk))
                page_element.setAttribute('name', page.name.replace('\\\\', '\\'))
    
    def set_module_translated_content(self, module_element, field):
        module_type = module_element.nodeName
        execute = {
           'textModule' : self.set_texts_for_text_module,
           'buttonModule' : self.set_texts_for_button_module,
           'choiceModule' : self.set_texts_for_choice_module,
           'orderingModule' : self.set_texts_for_ordering_module,
           'sourceListModule' : self.set_texts_for_source_list_module,
           'reportModule' : self.set_texts_for_report_module,
           'addonModule' : self.set_texts_for_addon_module
        }
        execute[module_type](module_element, field)
    
    def set_texts_for_text_module(self, module_element, field):
        if field.value:
            property_node = module_element.getElementsByTagName('text')
            if len(property_node) > 0:
                set_or_create_text_node(self.document, property_node[0], field.value)
            else:
                self.errors.append('Property Text not found.')
    
    def set_texts_for_button_module(self, module_element, field):
        property_node = module_element.getElementsByTagName('button')
        if len(property_node) > 0:
            property_node[0].setAttribute('text', field.value)
        else:
            self.errors.append('Property Title not found.')
    
    def set_texts_for_choice_module(self, module_element, field):
        index = int(field.list_index)
        property_nodes = module_element.getElementsByTagName('text')
        if len(property_nodes) > 0:
            if index >= len(property_nodes):
                new_property_node = property_nodes[0].parentNode.cloneNode(True)
                get_parent(property_nodes[0], 2).appendChild(new_property_node)
                property_nodes = module_element.getElementsByTagName('text')
            set_or_create_text_node(self.document, property_nodes[index], field.value)
        else:
            self.errors.append('Property Item not found.')
    
    def set_texts_for_ordering_module(self, module_element, field):
        index = int(field.list_index)
        property_nodes = module_element.getElementsByTagName('item')
        if len(property_nodes) > 0:
            if index >= len(property_nodes):
                new_property_node = property_nodes[0].cloneNode(True)
                property_nodes[0].parentNode.appendChild(new_property_node)
                property_nodes = module_element.getElementsByTagName('item')
            set_or_create_text_node(self.document, property_nodes[index], field.value)
        else:
            self.errors.append('Property Item not found.')
    
    def set_texts_for_source_list_module(self, module_element, field):
        list_index = int(field.name.split('-')[1])
        property_nodes = module_element.getElementsByTagName('item')
        if len(property_nodes) > 0:
            if list_index >= len(property_nodes):
                new_property_node = property_nodes[0].cloneNode(True)
                property_nodes[0].parentNode.appendChild(new_property_node)
                property_nodes = module_element.getElementsByTagName('item')

            if property_nodes[list_index].firstChild is None:
                cdata = self.document.createCDATASection('')
                property_nodes[list_index].appendChild(cdata)
            property_nodes[list_index].firstChild.data = field.value
        else:
            self.errors.append('Property Items not found.')
    
    def set_texts_for_report_module(self, module_element, field):
        labels = module_element.getElementsByTagName('label')
        property_found = False
        for label in labels:
            if label.getAttribute('name') == field.name:
                label.setAttribute('value', field.value)
                property_found = True
                continue
        if not property_found:
            info = 'Property ' + field.name + ' not found.'
            self.errors.append(info)

    def set_texts_for_addon_module(self, module_element, field):
        properties = module_element.getElementsByTagName('property')
        if is_list_type(field):
            list_properties = get_list_properties(properties, field.name)
            if len(list_properties) == 0:
                info = 'Property ' + field.name + ' not found.'
                self.errors.append(info)
            filtered_properties = get_list_properties_by_name(list_properties, field.list_name)
            if len(filtered_properties) == 0:
                info = 'Property ' + field.list_name + ' not found.'
                self.errors.append(info)
            index = int(field.list_index)
            if index >= len(filtered_properties):
                new_property_node = filtered_properties[0].parentNode.cloneNode(True)
                items_node = get_parent(filtered_properties[0], 1)
                items_node.appendChild(new_property_node)
                properties = module_element.getElementsByTagName('property')
                list_properties = get_list_properties(properties, field.name)
                filtered_properties = get_list_properties_by_name(list_properties, field.list_name)
            if filtered_properties[index].getAttribute('type') == 'string':
                filtered_properties[index].setAttribute('value', field.value)
            else:
                set_or_create_text_node(self.document, filtered_properties[index], field.value)
        else:
            property_element = get_property_by_name(properties, field.name)
            if property_element:
                if property_element.getAttribute('type') == 'string':
                    property_element.setAttribute('value', field.value)
                else:
                    set_or_create_text_node(self.document, property_element, field.value)
            else:
                info = 'Property ' + field.name + ' not found.'
                self.errors.append(info)

    def get_addons_fields_for_translation(self):
        addons_fields = {}

        addons_descriptors_xml = self.document.getElementsByTagName('addon-descriptor')

        with IcplayerZipped() as icplayer:
            for addon_descriptor in addons_descriptors_xml:
                addon_name = addon_descriptor.getAttribute('addonId')
                url_attribute = addon_descriptor.getAttribute('href')

                properties = icplayer.get_addon_properties(addon_name, url_attribute)

                addons_fields[addon_name] = set(properties)

        return addons_fields

    def get_module_elements(self, page):
        href = self.get_href_by_page_id(page.id)
        file_storage = get_file(href)
        xml = minidom.parseString(file_storage.contents)
        modules = []
        for module_type in _moduleTypes:
            modules.extend(xml.getElementsByTagName(module_type))
        return modules

    def get_module(self, module):
        execute = {
           'textModule' : self.get_text_module,
           'buttonModule' : self.get_button_module,
           'choiceModule' : self.get_choice_module,
           'orderingModule' : self.get_ordering_module,
           'sourceListModule' : self.get_source_list_module,
           'reportModule' : self.get_report_module
        }
        return handle_execution(execute, module)

    def get_text_module(self, module):
        text_nodes = module.getElementsByTagName('text')
        content = text_nodes[0].firstChild.data if text_nodes[0].hasChildNodes() else ''
        module_id = module.getAttribute('id')
        module = Module(module_id)
        if not is_empty(content):
            property_name = 'Text'
            module.fields = [Field(content, property_name, 'html')]
        return module
    
    def get_button_module(self, module):
        content = module.getElementsByTagName('button')[0].getAttribute('text')
        module_id = module.getAttribute('id')
        module = Module(module_id)
        if not is_empty(content):
            property_name = 'Title'
            module.fields = [Field(content, property_name, 'string')]
        return module
    
    def get_choice_module(self, module):
        contents = [text_element.firstChild.data for text_element in module.getElementsByTagName('text') if text_element.hasChildNodes()]
        module_id = module.getAttribute('id')
        property_name = 'Item'
        list_property_name = 'Text'
        module = Module(module_id)
        for counter, content in enumerate(contents):
            if not is_empty(content):
                module.fields.append(Field(content, property_name, 'html', list_property_name, counter))
        return module
    
    def get_ordering_module(self, module):
        contents = [item_element.firstChild.data for item_element in module.getElementsByTagName('item') if item_element.hasChildNodes()]
        property_name = 'Item'
        module_id = module.getAttribute('id')
        list_property_name = 'Text'
        module = Module(module_id)
        for counter, content in enumerate(contents):
            if not is_empty(content):
                module.fields.append(Field(content, property_name, 'html', list_property_name, counter))
        return module
    
    def get_source_list_module(self, module):
        elements = module.getElementsByTagName('item')
        if len(elements) > 0:
            if elements[0].hasChildNodes():
                contents = [item_element.firstChild.data for item_element in elements]
            elif elements[0].getAttribute("text"):
                contents = [item_element.getAttribute("text") for item_element in module.getElementsByTagName('item')]
            else:
                contents = []
        property_name = 'Items'
        module_id = module.getAttribute('id')
        module = Module(module_id)
        for counter, content in enumerate(contents):
            if not is_empty(content):
                module.fields.append(Field(content, property_name + '-' + str(counter), 'string'))
        return module
    
    def get_report_module(self, module):
        label_elements = module.getElementsByTagName('label')
        module_id = module.getAttribute('id')
        module = Module(module_id)
        for label in label_elements:
            content = label.getAttribute('value')
            if not is_empty(content):
                property_name = label.getAttribute('name')
                module.fields.append(Field(content, property_name, 'string'))
        return module
    
    def get_addon(self, module_element, addon_fields):
        properties = module_element.getElementsByTagName('property')
        counter = 0
        last_properties_name = (None, None)
        module_id = module_element.getAttribute('id')
        filtered_properties = get_properties_for_translation(properties, addon_fields)
        filtered_properties = sorted(filtered_properties, key=lambda property: property.getAttribute('name'))
        module = Module(module_id)
        for filtered in filtered_properties:
            content = get_content_from_property(filtered)
            if not is_empty(content):
                list_property_name = None
                list_property_index = None
                property_name = filtered.getAttribute('name')
                field_type = filtered.getAttribute('type')
                if parent_is_list(filtered):
                    parent = get_parent(filtered, 2)
                    list_property_name = property_name
                    property_name = parent.getAttribute('name')
                    counter, last_properties_name = calculate_counter(counter, last_properties_name, (property_name, list_property_name))
                    list_property_index = counter
                module.fields.append(Field(content, property_name, field_type, list_property_name, list_property_index))
        return module

    def update(self, difference, otherXML, user):
        if difference.get_type() == DifferenceType.PAGE_MISSING:
            page_element = otherXML.get_page_element_by_id(difference.page.id)
            href = otherXML.get_href_by_page_id(difference.page.id)
            page_copy = make_page_copy(href, user)
            page_copy.save()
            page_element.setAttribute('href', str(page_copy.pk))
            pages_element = self.document.getElementsByTagName('pages')[0]
            pages_element.appendChild(page_element)
            lesson = get_content(self.content_id)
            lesson.file.contents = self.print_document()
            lesson.file.save()
            return
        if difference.get_type() == DifferenceType.MODULE_MISSING:
            href = self.get_href_by_page_id(difference.page.id)
            page_file = get_file(href)
            page_fileXML = minidom.parseString(page_file.contents)
            modules_element = page_fileXML.getElementsByTagName('modules')[0]
            otherXML_module_elements = otherXML.get_module_elements(difference.page)
            module_element = otherXML.get_module_element_by_id(otherXML_module_elements, difference.module.id)
            modules_element.appendChild(module_element)
            page_file.contents = page_fileXML.toxml('UTF-8')
            page_file.save()
            return
        if difference.get_type() == DifferenceType.FIELD_MISSING:
            href = self.get_href_by_page_id(difference.page.id)
            page_file = get_file(href)
            page_fileXML = minidom.parseString(page_file.contents)
            modules_element = page_fileXML.getElementsByTagName('modules')[0]
            module_element = [module for module in modules_element.childNodes if module.getAttribute('id') == difference.module.id][0]
            self.set_module_translated_content(module_element, difference.field)
            page_file.contents = page_fileXML.toxml('UTF-8')
            page_file.save()
            return

class Xliff(object):
    def __init__(self, document):
        self.document = document

    def get_target_language(self):
        return self.document.getElementsByTagName('file')[0].getAttribute('target-language')
    
    def set_target_language(self, language):
        return self.document.getElementsByTagName('file')[0].setAttribute('target-language', language)

    def set_translated_content(self, value, group_id, trans_unit_id):
        group_element = self.get_group_element_by_id(group_id)
        trans_unit_element = self.get_trans_unit_element_by_id(trans_unit_id, group_element)
        target_element = trans_unit_element.getElementsByTagName('target')[0]
        set_or_create_text_node(self.document, target_element, value)

    def set_translated_page_name(self, page_name, page_id):
        group_element = self.get_group_element_by_id(page_id)
        group_element.setAttribute('id', page_name + '|' + page_id)

    def insert_texts_for_translation(self, pages, content_id):
        content = get_content(content_id)
        self.set_content_id(content)
        
        for page in pages:
            group = self.insert_group_element(page)
            for module in page.modules:
                for field in module.fields:
                    trans_unit = self.insert_trans_unit_element(group, field, module)
                    self.insert_source(trans_unit, field)
                    self.insert_target(trans_unit, field)
    
    def _get_file_element(self):
        file_elements = self.document.getElementsByTagName('file')
        if len(file_elements) == 0:
            raise NodeNotFoundException('\'File\'')
        file_element = file_elements[0]
        return file_element
    
    def set_content_id(self, content):
        file_element = self._get_file_element()
        file_element.setAttribute('original', str(content.id))
    
    def set_localized_version(self, version):
        file_element = self._get_file_element()
        file_element.setAttribute('localized-version', str(version))
        
    def set_original_version(self, version):
        file_element = self._get_file_element()
        file_element.setAttribute('original-version', str(version))
    
    def _get_file_attribute_value(self, attribute):
        file_elements = self.document.getElementsByTagName('file')
        if len(file_elements) == 0:
            raise NodeNotFoundException('\'File\'')
        file_element = file_elements[0]
        version = file_element.getAttribute(attribute)
        pattern = "[\d]+"
        match = re.match(pattern, version)
        if not match:
            raise ContentException('Your Xliff file has no information about version or it\'s invalid.')
        return version
    
    def get_content_id(self):
        content_id = self._get_file_attribute_value('original')
        return int(content_id)

    def get_localized_version(self):
        version = self._get_file_attribute_value('localized-version')
        return int(version)

    def get_original_version(self):
        version = self._get_file_attribute_value('original-version')
        return int(version)
    
    def insert_metadata_element(self, content_id):
        page = Page(name='metadata', page_id='metadata')
        group = self.insert_group_element(page)
        content = get_content(content_id)
        metadata = content.get_metadata()
        self.set_metadata_element(group, metadata)

    def set_metadata_element(self, group, metadata):
        for k, v in list(metadata.items()):
            if not is_empty(v):
                trans_unit = self.document.createElement('trans-unit')
                trans_unit.setAttribute('id', k)
                group.appendChild(trans_unit)
                field = Field(v, k)
                self.insert_source(trans_unit, field)
                self.insert_target(trans_unit, field)

    def get_metadata_from_metadata_element(self):
        metadata_node = self.get_group_element_by_id('metadata')
        metadata = {'title' : '',
                    'tags' : '',
                    'description' : '',
                    'short_description' : ''}

        for target in metadata_node.getElementsByTagName('target'):
            key = target.parentNode.getAttribute('id')
            metadata[key] = re.sub('</?it.*?>', '', target.firstChild.data)

        return metadata

    def get_group_element_by_id(self, group_id):
        groups = self.get_group_elements()
        for group in groups:
            if group.getAttribute('id').split('|')[1] == group_id:
                return group
        return None
        
    def get_trans_unit_element_by_id(self, trans_unit_id, group_element):
        for trans_unit_element in group_element.getElementsByTagName('trans-unit'):
            if trans_unit_element.getAttribute('id') == trans_unit_id:
                return trans_unit_element
        return None
        
    def insert_group_element(self, page):
        body = self.document.getElementsByTagName('body')[0]
        group = self.document.createElement('group')
        group.setAttribute('id', page.name + '|' + page.id)
        group.setAttribute('folder_name', page.folder_name)
        body.appendChild(group)
        return group
    
    def get_group_elements(self, group_filter=None):
        groups = self.document.getElementsByTagName('group')
        if group_filter:
            groups = [group for group in groups if group_filter(group)]
        return groups
    
    def insert_trans_unit_element(self, group_element, field, module):
        trans_unit = self.document.createElement('trans-unit')
        id_string = create_id_string(field, module)
        trans_unit.setAttribute('id', id_string)
        group_element.appendChild(trans_unit)
        return trans_unit

    def get_pages_with_modules_and_fields(self, groups):
        pages = []
        for group in groups:
            modules = []
            trans_units = group.getElementsByTagName('trans-unit')
            name = group.getAttribute('id').split('|')[0].replace('\\', '\\\\')
            page_id = group.getAttribute('id').split('|')[1]
            folder_name = group.getAttribute('folder_name')
            page = Page(name=name, page_id=page_id, folder_name=folder_name)

            for trans_unit in trans_units:
                string_id = trans_unit.getAttribute('id')
                module_params, property_name, field_type, list_property_name, list_property_index = resolve_id_string(string_id)
                targets = trans_unit.getElementsByTagName('target')
                if len(targets) == 0:
                    continue
                content = targets[0]
                flat_content = ''
                for child in content.childNodes:
                    flat_content = flat_content + child.toxml()
                content = re.sub('</?it.*?>', '', flat_content)
                content = content.replace("&gt;", ">").replace("&quot;", "\"").replace("&lt;", "<").replace("&amp;", "&")
                if len(modules) > 0 and module_params.split(':')[0] == modules[-1].id:
                    module = modules[-1]
                else:
                    module_params = module_params.split(':')
                    module = Module(module_params[0], module_params[1])
                module.fields.append(Field(content, property_name, field_type, list_property_name, list_property_index))
                if module not in modules:
                    modules.append(module)
            page.modules = modules
            if len(page.modules) > 0:
                pages.append(page)
        return pages

    def insert_source(self, trans_unit, field):
        source = self.document.createElement('source')
        text_node = XliffXMLNode(field.value, field.type)
        source.appendChild(text_node)
        trans_unit.appendChild(source)

    def insert_target(self, trans_unit, field):
        target = self.document.createElement('target')
        target.setAttribute('state', 'needs-translation')
        text_node = XliffXMLNode(field.value, field.type)
        target.appendChild(text_node)
        trans_unit.appendChild(target)

    def print_document(self):
        return self.document.toxml(encoding='UTF-8')

    def validate_size(self):
        xml = self.document.toxml(encoding='UTF-8')
        if len(xml) > FILE_SIZE_LIMIT:
            raise ContentTooBigException('Content size is %s' % len(xml))

class Page(object):
    def __init__(self, name, page_id, folder_name=''):
        self.name = name
        self.id = page_id
        self.folder_name = folder_name
        self.modules = []
    
    def get_module(self, searching_module):
        for module in self.modules:
            if module.id == searching_module.id:
                return module
        return None

class Module(object):
    def __init__(self, module_id, name=None):
        self.id = module_id
        self.name = name
        self.fields = []
    
    def get_field(self, searching_field):
        for field in self.fields:
            if field.name == searching_field.name and field.list_name == searching_field.list_name and field.list_index == searching_field.list_index:
                return field
        return None

    def __str__(self):
        return '<ID: %s, Name: %s>' % (self.id, self.name)

class Field(object):
    def __init__(self, value, name, field_type=None, list_name=None, list_index=None):
        self.value = value
        self.name = name
        self.type = field_type
        self.list_name = list_name # if field is type list
        self.list_index = list_index # index on list if field is type list
   
    def __repr__(self):
        return '<Name: %s, Value: %s, Type: %s>' % (self.name, self.value, self.type)
   
class DifferenceType():
    PAGE_MISSING = 1
    MODULE_MISSING = 2
    FIELD_MISSING = 3
   
class Difference(object):
    def __init__(self, msg, page, module, field):
        self.msg = msg
        self.page = page
        self.module = module
        self.field = field
        
    def get_type(self):
        if len([x for x in (self.page, self.module, self.field) if x != None]) == 1:
            return DifferenceType.PAGE_MISSING
        
        if len([x for x in (self.page, self.module, self.field) if x != None]) == 2:
            return DifferenceType.MODULE_MISSING
        
        if len([x for x in (self.page, self.module, self.field) if x != None]) == 3:
            return DifferenceType.FIELD_MISSING

class Comparer(object):
    def __init__(self, lessonX, pagesX, lessonY, pagesY):
        self.pagesX = pagesX # pages from original lesson
        self.pagesY = pagesY # pages from localized lesson
        self.lessonX = lessonX
        self.lessonY = lessonY
        self.differences = []
    
    def get_page(self, searching_page):
        for page in self.pagesY:
            if page.id == searching_page.id:
                return page
        return None
    
    def get_messages(self):
        return [diff.msg for diff in self.differences]
    
    def _create_page_missing_message(self, page):
        return 'Page with name %(page)s was NOT found in lesson %(lesson)s.' % { 'page' : page.name, 'lesson' : self.lessonY.title }

    def _create_module_missing_message(self, page, module):
        return 'Module with name %(module)s was NOT found in lesson %(lesson)s on page %(page)s.' % { 'module' : module.id, 'lesson' : self.lessonY.title, 'page' : page.name }
    
    def _create_field_missing_message(self, page, module):
        return 'Fields in module %(module)s has been changed in lesson %(lesson)s on page %(page)s.' % { 'module' : module.id, 'lesson' : self.lessonY.title, 'page' : page.name }
    
    def compare(self):
        for pageX in self.pagesX:
            pageY = self.get_page(pageX)
            if pageY == None:
                msg = self._create_page_missing_message(pageX)
                difference = Difference(msg, pageX, None, None)
                self.differences.append(difference)
                continue
            for moduleX in pageX.modules:
                moduleY = pageY.get_module(moduleX)
                if moduleY == None:
                    msg = self._create_module_missing_message(pageY, moduleX)
                    difference = Difference(msg, pageX, moduleX, None)
                    self.differences.append(difference)
                    continue
                for fieldX in moduleX.fields:
                    if moduleY.get_field(fieldX) == None:
                        msg = self._create_field_missing_message(pageY, moduleX)
                        difference = Difference(msg, pageX, moduleX, fieldX)
                        self.differences.append(difference)
                        continue

class XliffXMLNode(Childless, Node):
    nodeType = Node.TEXT_NODE
    next_id = 1

    def __init__(self, data, type):
        self.data = data
        self.type = type

    def writexml(self, writer, indent="", addindent="", newl=""):
        from BeautifulSoup import BeautifulSoup

        if self.type == 'html':
            # Wrap data by div tag and after escaping remove this div tag
            bs = str(BeautifulSoup("<div>{}</div>".format(self.data.encode('utf-8'))))[5:-6]
            stripped_entities = bs.replace("&", "&amp;").replace("\"", "&quot;")

        else:
            data = str(self.data)
            stripped_entities = escape(data)
        replaced = re.sub(r'<((?!<).|\n)*?>', self._replace_match, str(stripped_entities))
        writer.write(replaced)

    def _replace_match(self, matchobj):
        current_match = matchobj.group(0)
        pos = 'open'
        if current_match[1] == '/':
            pos = 'close'

        open_tag = '<it id="%s" pos="%s">' % (self.next_id, pos)
        value = current_match.replace("<", "&lt;").replace(">", "&gt;")
        close_tag = '</it>'
        self.next_id = self.next_id + 1
        return open_tag + value + close_tag