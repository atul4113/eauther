import copy
import re
from abc import abstractmethod
from xml.dom.minidom import Document, Node
from src.mauthor.lessons_parsers.property_changer.parsers.parser import Parser
from src.mauthor.lessons_parsers.property_changer.util import get_property_by_name, get_items_tag
from src.mauthor.lessons_parsers.property_changer.models import AddonPropertyModel, DefaultFrontEndPropertyModel, ListFrontEndPropertyModel, StaticListFrontEndPropertyModel, StaticRowFrontEndPropertyModel


# noinspection PyClassHasNoInit
class AddonModelParser(object):
    MODEL = DefaultFrontEndPropertyModel

    @classmethod
    def parse_model(cls, property_model):
        children = []
        for property in property_model.property_xml.childNodes:
            if property.nodeType == Node.TEXT_NODE:
                continue

            property_child_model = AddonPropertyModel(property)
            parser = PropertyParserFactory.get(property_child_model.get_property_name())
            if parser is not None:
                children.append(parser.parse_model(property_child_model))

        return cls.MODEL(property_model.get_name(), children)


# noinspection PyMethodMayBeStatic
class AddonPropertyParser(Parser):
    TYPE = 'init'

    @abstractmethod
    def parse(self, config, property_model, depth=0, row_number=None):
        pass

    def _passed_complete_model_log(self):
        self.logger.add_log(action="PASSED_COMPLETE_MODEL",
                            type="WARNING",
                            message="Undefined property or list didn't exist")


class BooleanParserAddon(AddonPropertyParser, AddonModelParser):
    TYPE = 'boolean'
    AVAILABLE_VALUES = {"true": "True",
                        "false": "False"}

    def parse(self, config, property_model, depth=0, row_number=None):
        if config['new_value'].lower() in self.AVAILABLE_VALUES:
            self._change_log(property_model.get_value(), self.AVAILABLE_VALUES[config['new_value'].lower()], property_model.get_name(), row_number=row_number)
            property_model.set_value(self.AVAILABLE_VALUES[config['new_value'].lower()])
            return True
        else:
            self._non_valid_log('Value don\'t match to "true" or "false"')


class StringParserAddon(AddonPropertyParser, AddonModelParser):
    TYPE = 'string'

    def parse(self, config, property_model, depth=0, row_number=None):
        self._change_log(property_model.get_value(), config['new_value'], property_model.get_name(), row_number=row_number)
        property_model.set_value(config['new_value'])
        return True


class ListParserAddon(AddonPropertyParser, AddonModelParser):
    TYPE = 'list'
    MODEL = ListFrontEndPropertyModel

    def parse(self, config, property_model, depth=0, row_number=None):
        changed = False
        items_tag = get_items_tag(property_model.property_xml)
        rows_numbers_to_parse = self._get_rows_numbers(config, items_tag)

        default_value_dictionary = copy.deepcopy(config)
        default_value_dictionary['new_value'] = config['default_value']
        for row_number, _ in enumerate(items_tag.childNodes, start=1):
            new_changed = self._parse_row(row_number, items_tag, depth, default_value_dictionary, property_model, False)
            changed = changed or new_changed

        for row_number in rows_numbers_to_parse:
            new_changed = self._parse_row(row_number, items_tag, depth, config, property_model)
            changed = changed or new_changed

        return changed

    def _get_rows_numbers(self, config, items_tag):
        match = re.match("^\[(\d+|start)-(\d+|end)]$", config['list_row_number'])
        if match:
            from_value = match.group(1)
            to_value = match.group(2)
            if from_value == 'start':
                from_value = 1
            if to_value == 'end':
                to_value = len(items_tag.childNodes)
            values = list(range(int(from_value), int(to_value) + 1))

        else:
            values = [int(value) for value in config['list_row_number'].split(',')]

        return values



    def _parse_row(self, row_number, items_xml, depth, config, property_model, parse_if_dont_completed=True):
        if row_number <= len(items_xml.childNodes):
            property_name = config['property_name'].split('/')
            item = items_xml.childNodes[row_number - 1]
            item_addon_property_model = AddonPropertyModel(item,
                                                           property_model.model_xml,
                                                           path=property_model.path,
                                                           template_xml=property_model.template_xml
                                                           )
            property_model = item_addon_property_model.get_property_model_by_name(property_name[depth + 2], self.logger)
            if property_model is None:
                self._passed_complete_model_log()
                return False
            model_was_completed = item_addon_property_model.model_was_completed
            parser = PropertyParserFactory.get(property_model.get_property_name())
            if parser and parse_if_dont_completed:
                return parser(logger=self.logger).parse(config, property_model, depth=depth + 2, row_number=row_number)
            elif parser and model_was_completed and not parse_if_dont_completed:
                return parser(logger=self.logger).parse(config, property_model, depth=depth + 2, row_number=row_number)
            return False
        else:
            self._non_valid_log('OutOfListRange,"max value: %d, given: %d"' % (len(items_xml.childNodes), row_number))


class StaticListParserAddon(AddonPropertyParser, AddonModelParser):
    TYPE = 'staticlist'
    MODEL = StaticListFrontEndPropertyModel

    def parse(self, config, property_model, depth=0, row_number=None):
        property_name = config['property_name'].split('/')
        items = get_items_tag(property_model.property_xml)
        for item in items.childNodes:
            item_addon_property_model = AddonPropertyModel(item,
                                                           property_model.model_xml,
                                                           path=property_model.path,
                                                           template_xml=property_model.template_xml)
            child_property_model = item_addon_property_model.get_property_model_by_name(property_name[depth + 1], self.logger)
            if child_property_model is not None:
                parser = PropertyParserFactory.get(child_property_model.get_property_name())
                if parser:
                    return parser(logger=self.logger).parse(config, child_property_model, depth + 2)
                else:
                    return False
        return False


class StaticRowParserAddon(AddonPropertyParser, AddonModelParser):
    TYPE = 'staticrow'
    MODEL = StaticRowFrontEndPropertyModel

    def parse(self, config, property_model, depth=0, row_number=None):
        property_name = config['property_name'].split('/')
        name = property_name[depth]

        for item in property_model.property_xml.childNodes:
            item_addon_property_model = AddonPropertyModel(item,
                                                           property_model.model_xml,
                                                           path=property_model.path,
                                                           template_xml=property_model.template_xml)
            child_property_model = item_addon_property_model.get_property_model_by_name(name, self.logger)
            if child_property_model is not None:
                parser = PropertyParserFactory.get(child_property_model.get_property_name())
                if parser:
                    return parser(logger=self.logger).parse(config, child_property_model, depth=depth + 1)


class EnumParserAddon(AddonPropertyParser, AddonModelParser):
    TYPE = 'enum'

    def parse(self, config, property_model, depth=0, row_number=None):
        new_value = config['new_value']
        if self.__is_valid(property_model.get_property_type(), new_value):
            self._change_log(property_model.get_value(), new_value, property_model.get_name(), row_number=row_number)
            property_model.set_value(new_value)
            return True
        return False

    def __is_valid(self, properties_value, new_value):
        # removing brackets {}
        unbracket = properties_value[1:-1]
        values = [value.strip() for value in unbracket.split(',')]

        if new_value.strip() in values:
            return True

        self._non_valid_log("New value is not in available values: %s" % properties_value)
        return False


# noinspection PyMethodMayBeStatic
class EditableSelectParserAddon(AddonPropertyParser, AddonModelParser):
    TYPE = 'editableselect'

    def parse(self, config, property_model, depth=0, row_number=None):
        property_name = config['property_name'].split('/')

        if len(property_name) == depth + 1:     # change which value is selected
            return self.__change_selected_value(property_model, config['new_value'], row_number)
        else:
            return self.__change_child_value(property_model, property_name[depth + 1], config, depth, row_number)

    def __change_child_value(self, property_model, name, config, depth, row_number):
        property_model = property_model.get_property_model_by_name(name, self.logger)
        if property_model is None:
            self._passed_complete_model_log()
            return False
        parser = PropertyParserFactory.get(property_model.get_property_name())
        if parser:
            return parser(logger=self.logger).parse(config, property_model, depth=depth + 2, row_number=row_number)

        return False

    def __change_selected_value(self, property_model, new_value, row_number):
        value = self.__get_selected_value(property_model, new_value)
        if value:
            self._change_log(property_model.get_value(), value, property_model.get_name(), row_number=row_number)
            property_model.set_value(value)
            return True
        self._non_valid_log("Selected value is not valid")
        return False

    def __get_selected_value(self, property_model, new_value):
        for property_xml in property_model.property_xml.childNodes:
            property_node = AddonPropertyModel(property_xml)
            if property_node.get_name().lower() == new_value.lower():
                return property_node.get_display_name()
        return False


class TextParserAddon(AddonPropertyParser, AddonModelParser):
    TYPE = 'text'
    CREATE = Document().createTextNode

    def parse(self, config, property_model, depth=0, row_number=None):
        new_value = config['new_value']

        if property_model.property_xml.firstChild is None:
            text_node = self.CREATE('')
            property_model.property_xml.appendChild(text_node)

        self._change_log(property_model.property_xml.firstChild.wholeText, new_value, property_model.get_name(), row_number=row_number)
        property_model.property_xml.firstChild.data = new_value
        return True


class EventParser(TextParserAddon):
    TYPE = 'event'


class FileParser(StringParserAddon):
    TYPE = 'file'


class AudioParser(StringParserAddon):
    TYPE = 'audio'


class VideoParser(StringParserAddon):
    TYPE = 'video'


class ImageParser(StringParserAddon):
    TYPE = 'image'


class HTMLParser(TextParserAddon):
    TYPE = 'html'
    CREATE = Document().createCDATASection


class NarrationParser(TextParserAddon):
    TYPE = 'narration'


PropertyParserFactory = {
    'list': ListParserAddon,
    'boolean': BooleanParserAddon,
    'string': StringParserAddon,
    'text': TextParserAddon,
    'staticrow': StaticRowParserAddon,
    'editableselect': EditableSelectParserAddon,
    'staticlist': StaticListParserAddon,
    'enum': EnumParserAddon,
    'html': HTMLParser,
    'image': ImageParser,
    'video': VideoParser,
    'audio': AudioParser,
    'file': FileParser,
    'event': EventParser,
    'narration': NarrationParser
}


