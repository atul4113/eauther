import xml.dom.minidom as minidom

import re
from libraries.utility.helpers import get_object_or_none
from lorepo.filestorage.models import FileStorage
from .util import number_in_regex_range, get_property_by_name, get_element_by_tag_name, get_addon_model


class Validator(object):
    ELEMENT_TYPE = 'INIT'

    def get_passed_message(self, href, message, **kwargs):
        log = {
            "action": 'PASSED',
            "type": 'INFO',
            "message": message,
            "page_id": href,
            "element_type": self.ELEMENT_TYPE
        }
        return dict(list(log.items()) + list(kwargs.items()))

    def return_error(self, href, message, **kwargs):
        return False, self.get_passed_message(href, message, **kwargs)

    def valid(self, config):
        self.validated = True

        for validator in self.validators:
            is_valid, message = validator(config)
            if not is_valid:
                return is_valid, message

        self.is_valid = True
        return True, None


# noinspection PyMethodMayBeStatic
class PageModel(Validator):
    ELEMENT_TYPE = 'Page'

    def __init__(self, page_row, index):
        self.href = page_row.getAttribute('href')
        self.name = page_row.getAttribute('name')
        self.is_in_commons = self.__is_in_commons(page_row)
        self.number = index + 1
        self.validated = False
        self.page_xml = None
        self.page = None
        self.is_valid = None

        if self.is_in_commons:
            self.__get_index_relative_to_commons(page_row)

        self.validators = [
                self.__valid_page_name,
                self.__valid_page_is_common,
                self.__valid_page_number
            ]

    def complete_model(self):
        if not self.validated:
            raise ValueError('Before complete, model must be validated!')

        if not self.is_valid:
            raise ValueError('Model is not valid!')

        self.page_xml, self.page = self.__get_page()

    def __is_in_commons(self, page_row):
        parent = page_row.parentNode
        if parent.hasAttribute('name'):
            if parent.getAttribute('name') == 'commons':
                return True
        return False

    def __get_index_relative_to_commons(self, page_row):
        parent = page_row.parentNode
        for index, page in enumerate(parent.childNodes):
            if page_row is page:
                self.number = index + 1
                return

        raise Exception("Cant find page in commons")

    def __get_page(self):
        page = get_object_or_none(FileStorage, id=self.href)
        return minidom.parseString(page.contents), page

    def get_addons(self):
        return self.page_xml.getElementsByTagName('addonModule')

    def get_modules(self, tag_name):
        return self.page_xml.getElementsByTagName(tag_name)

    def __valid_page_name(self, config):
        if config["parse_all_pages_name"]:
            return True, None

        if re.search(config['page_name'], self.name):
            return True, None
        else:
            return self.return_error(self.href, 'Page name not match to pattern')

    def __valid_page_is_common(self, config):
        parse_commons_and_page_not_in_commons = config['parse_commons'] and not self.is_in_commons
        dont_parse_commons_and_page_in_commons = not config['parse_commons'] and self.is_in_commons

        if parse_commons_and_page_not_in_commons or dont_parse_commons_and_page_in_commons:
            return self.return_error(self.href, 'Page is%s in commons' % ('not' if config['parse_commons'] else ''))

        return True, None

    def __valid_page_number(self, config):
        if number_in_regex_range(self.number, config['page_number']):
            return True, None

        return self.return_error(self.href, 'Page number don\'t match to available numbers')


class AddonModel(Validator):
    ELEMENT_TYPE = 'Addon'
    MODELS = {}

    def __init__(self, addon_xml):
        self.addon_xml = addon_xml
        self.addon_name = addon_xml.getAttribute('addonId')
        self.id = addon_xml.getAttribute('id')

        self.__set_model()

        self.validators = [
            self.__valid_addon_id,
            self.__valid_addon_name
        ]

    def get_property_model(self):
        properties = self.addon_xml.getElementsByTagName('properties')[0]
        return AddonPropertyModel(properties, AddonModel.MODELS.get(self.addon_name))

    def __set_model(self):
        if AddonModel.MODELS.get(self.addon_name) is None:
            model = get_addon_model(self.addon_name)
            AddonModel.MODELS[self.addon_name] = model

    def __valid_addon_name(self, config):
        if self.addon_name == config['addon_name']:
            return True, None

        return self.return_error(None, 'Addon or module name don\'t match', addon_id=self.id)

    def __valid_addon_id(self, config):
        if config['parse_all_addons']:
            return True, None

        if re.search(config['addon_ID'], self.id):
            return True, None

        return self.return_error(None, 'Addon or module ID don\'t match', addon_id=self.id)


class ModuleModel(Validator):
    ELEMENT_TYPE = 'Module'

    def __init__(self, module_xml):
        self.id = module_xml.getAttribute('id')
        self.module_xml = module_xml
        self.validators = [
            self.__valid_addon_id
        ]

    def get_element(self, tag_name):
        return self.get_all_elements(tag_name)[0]

    def get_all_elements(self, tag_name):
        return self.module_xml.getElementsByTagName(tag_name)

    def __valid_addon_id(self, config):
        if config['parse_all_addons']:
            return True, None

        if re.search(config['addon_ID'], self.id):
            return True, None

        return self.return_error(None, 'Addon or module ID don\'t match', addon_id=self.id)


class AddonPropertyModel(Validator):
    ELEMENT_TYPE = 'PropertyModel'

    def __init__(self, property_xml, model_xml=None, template_xml=None, path=[]):
        self.property_xml = property_xml
        self.model_xml = model_xml
        self.template_xml = template_xml
        self.path = path[:]
        self.model_was_completed = False

        if property_xml.tagName.lower() == 'property':
            self.path.append(property_xml.getAttribute('name'))
            if property_xml.getAttribute('type').lower() == 'list':
                self.template_xml = get_element_by_tag_name(property_xml, 'template')

    def get_property_name(self):
        if self.get_property_type().lower()[0] == '{':
            return 'enum'
        return self.get_property_type().lower()

    def get_property_type(self):
        return self.property_xml.getAttribute('type')

    def get_value(self):
        return self.property_xml.getAttribute('value')

    def set_value(self, new_value):
        self.property_xml.setAttribute('value', new_value)

    def get_name(self):
        return self.property_xml.getAttribute('name')

    def get_display_name(self):
        return self.property_xml.getAttribute('displayName')

    def get_property_model_by_name(self, name, logger):
        property_xml = get_property_by_name(self.property_xml, name)
        if property_xml is None:
            self.__complete_property(name, logger)
            property_xml = get_property_by_name(self.property_xml, name)

        return AddonPropertyModel(property_xml,
                                  get_property_by_name(self.model_xml, name),
                                  path=self.path,
                                  template_xml=self.template_xml) if property_xml is not None else None

    def __complete_property(self, name, logger):
        model_property = get_property_by_name(self.model_xml, name)
        if model_property is None:
            return
        if model_property.getAttribute('type').lower() in ['list', 'staticlist', 'staticrow']:
            return

        if self.template_xml is not None:
            self.__update_template(self.template_xml, self.path[1:] + [name], self.__create_property_from_model_property(model_property))
        self.property_xml.appendChild(self.__create_property_from_model_property(model_property))
        logger.add_log(action="ADDED_NEW_PROPERTY",
                       type="INFO",
                       property_name="%s" % name,
                       message="Added new property to model")
        self.model_was_completed = True

    def __create_property_from_model_property(self, model_property):
        doc = minidom.Document()
        new_property = doc.createElement('property')
        new_property.setAttribute('value', '')
        new_property.setAttribute('type', model_property.getAttribute('type'))
        new_property.setAttribute('name', model_property.getAttribute('name'))
        new_property.setAttribute('displayName', model_property.getAttribute('displayName'))
        if model_property.getAttribute('displayName') is None or model_property.getAttribute('displayName') == "":
            new_property.setAttribute('displayName', model_property.getAttribute('name'))
        return new_property


    def __update_template(self, property_xml, path, new_property):
        if len(path) == 1:
            child_property_xml = get_property_by_name(property_xml, path[0])
            if child_property_xml is None:
                property_xml.appendChild(new_property)
        else:
            property_xml = get_property_by_name(property_xml, path[0])
            self.__update_template(property_xml, path[1:], new_property)

    def valid(self, config=None):
        return self.property_xml is not None, None


class DefaultFrontEndPropertyModel(object):
    EDITABLE = True
    IS_LIST = False

    def __init__(self, name, children=[]):
        self.name = name
        self.children_model = children
        self.isEditable = self.EDITABLE
        self.isList = self.IS_LIST

    def get_model(self):
        return {
            'children': [child.get_model() for child in self.children_model],
            'name': self.name,
            'isEditable': self.isEditable,
            'isList': self.isList
        }


class ListFrontEndPropertyModel(DefaultFrontEndPropertyModel):
    EDITABLE = False
    IS_LIST = True


class StaticListFrontEndPropertyModel(DefaultFrontEndPropertyModel):
    EDITABLE = False


class StaticRowFrontEndPropertyModel(DefaultFrontEndPropertyModel):
    EDITABLE = False
