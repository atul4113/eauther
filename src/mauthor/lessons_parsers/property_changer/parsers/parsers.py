from abc import abstractmethod

from django.http import Http404
from src.mauthor.lessons_parsers.property_changer.parsers.properties_parsers import PropertyParserFactory
from src.mauthor.lessons_parsers.property_changer.util import number_in_regex_range, get_addon_model
from src.mauthor.lessons_parsers.property_changer.models import AddonModel, AddonPropertyModel, DefaultFrontEndPropertyModel, ListFrontEndPropertyModel, ModuleModel,StaticListFrontEndPropertyModel
from src.mauthor.lessons_parsers.property_changer.parsers.parser import Parser
from xml.dom.minidom import Document
from src.mauthor.lessons_parsers.property_changer.parsers.properties_parsers import AddonModelParser


# noinspection PyMethodMayBeStatic
class AddonParser(object):
    def __init__(self, name=None, logger=None):
        self.logger = logger
        self.name = name

    def parse(self, config, page_model):
        addons = page_model.get_addons()
        changed = False
        for addon in addons:
            addon_model = AddonModel(addon)
            is_valid, message = addon_model.valid(config)
            if is_valid:
                self.logger.add_log(type="INFO",
                                    action="WORKING_ON_ADDON/MODULE",
                                    addon_id=addon.getAttribute('id'))
                new_changed = self.__parse_properties(config, addon_model)
                changed = changed or new_changed
            else:
                self.logger.add_log(**message)
        return changed

    def parse_model(self):
        if self.name is not None:
            addon_model = get_addon_model(self.name)
        else:
            raise Http404()
        return AddonModelParser.parse_model(AddonPropertyModel(addon_model)).get_model()

    def __parse_properties(self, config, addon_model):
        property_name = config['property_name'].split('/')[0]

        addon_property_model = addon_model.get_property_model()
        property_model = addon_property_model.get_property_model_by_name(property_name, self.logger)
        if property_model is None:
            self.logger.add_log(action="PASSED_COMPLETE_MODEL",
                                type="WARNING",
                                message="Undefined property or list didn't exist")
            return False

        parser = PropertyParserFactory.get(property_model.get_property_name())
        if parser:
            return parser(logger=self.logger).parse(config, property_model)
        return False


class ModuleModelParser(object):
    MODEL = None

    @classmethod
    def parse_model(cls):
        return DefaultFrontEndPropertyModel(name='null', children=cls.MODEL).get_model()


class ModuleParser(Parser):
    TAG_NAME = 'init'

    def __init__(self, logger=None):
        super(ModuleParser, self).__init__(logger)
        self.logger = logger

    def parse(self, config, page_model):
        modules = page_model.get_modules(self.TAG_NAME)
        changed = False

        for module in modules:
            module_model = ModuleModel(module)
            is_valid, message = module_model.valid(config)
            if is_valid:
                self.logger.add_log(type="INFO",
                                    action="WORKING_ON_ADDON/MODULE",
                                    addon_id=module_model.id)
                changed = self.dispatch(module_model, config) or changed   # There must be "change = function or change"
            else:
                self.logger.add_log(**message)
        return changed

    @abstractmethod
    def dispatch(self, module_model, config):
        pass

    def _change_cdata_property(self, element, new_value, property_name, row_number=None):
        if element.firstChild is None:
            CDATA_node = Document().createCDATASection('')
            element.appendChild(CDATA_node)

        self._change_log(element.firstChild.wholeText, new_value, property_name, row_number=row_number)
        element.firstChild.data = new_value
        return True

    def _change_property(self, element, new_value, attribute_name, row_number=None):
        self._change_log(element.getAttribute(attribute_name), new_value, attribute_name, row_number=row_number)
        element.setAttribute(attribute_name, new_value)
        return True

    def _change_boolean_value(self, element, new_value, attribute_name):
        if new_value.lower() not in ['true', 'false']:
            self._non_valid_log('New value must be: "true" or "false"')
            return False

        return self._change_property(element, new_value.lower(), attribute_name)


class SpeechTextModuleParser(object):
    SPEECH_TEXT_ELEMENT = ""
    SPEECH_TEXT_ATTRIBUTE_NAMES = {}

    def _parse_speech_text(self, module_model, config):
        new_value = config['new_value']
        property_name = config['property_name']
        path = property_name.split('/')
        attribute_name = self.SPEECH_TEXT_ATTRIBUTE_NAMES.get(path[-1])
        element = module_model.get_element(self.SPEECH_TEXT_ELEMENT)
        return self._change_property(element, new_value, attribute_name)


class EmptyModuleParser(ModuleParser):
    def dispatch(self, module_model, config):
        return False


class TextModuleParser(ModuleModelParser, ModuleParser, SpeechTextModuleParser):
    TAG_NAME = 'textModule'
    SPEECH_TEXT_ELEMENT = 'text'

    SPEECH_TEXT_ITEM = [
        DefaultFrontEndPropertyModel('Number'),
        DefaultFrontEndPropertyModel('Gap'),
        DefaultFrontEndPropertyModel('Dropdown'),
        DefaultFrontEndPropertyModel('Correct'),
        DefaultFrontEndPropertyModel('Wrong'),
        DefaultFrontEndPropertyModel('Empty'),
        DefaultFrontEndPropertyModel('Inserted'),
        DefaultFrontEndPropertyModel('Removed'),
    ]

    MODEL = [
        DefaultFrontEndPropertyModel('Gap type'),
        DefaultFrontEndPropertyModel('Gap width'),
        DefaultFrontEndPropertyModel('Gap max length'),
        DefaultFrontEndPropertyModel('Is activity'),
        DefaultFrontEndPropertyModel('Is disabled'),
        DefaultFrontEndPropertyModel('Case sensitive'),
        DefaultFrontEndPropertyModel('Ignore punctuation'),
        DefaultFrontEndPropertyModel('Open external link in'),
        DefaultFrontEndPropertyModel('Text'),
        DefaultFrontEndPropertyModel('Keep Original Order'),
        DefaultFrontEndPropertyModel('Clear placeholder on focus'),
        DefaultFrontEndPropertyModel('Value type'),
        DefaultFrontEndPropertyModel('Block wrong answers'),
        DefaultFrontEndPropertyModel('User action events'),
        StaticListFrontEndPropertyModel(name='Speech Text', children=SPEECH_TEXT_ITEM),
    ]

    SPEECH_TEXT_ATTRIBUTE_NAMES = {
        'Number': 'number',
        'Gap': 'gap',
        'Dropdown': 'dropdown',
        'Correct': 'correct',
        'Wrong': 'wrong',
        'Empty': 'empty',
        'Inserted': 'insert',
        'Removed': 'removed',
    }

    TEXT_ATTRIBUTE_NAMES = {
        'Gap width': 'gapWidth',
        'Gap max length': 'gapMaxLength',
    }

    BOOLEAN_ATTRIBUTE_NAMES = {
        'Is activity': 'isActivity',
        'Is disabled': 'isDisabled',
        'Case sensitive': 'isCaseSensitive',
        'Ignore punctuation': 'isIgnorePunctuation',
        'Keep Original Order': 'isKeepOriginalOrder',
        'Clear placeholder on focus': 'isClearPlaceholderOnFocus',
        'Block wrong answers': 'blockWrongAnswers',
        'User action events': 'userActionEvents'
    }

    def dispatch(self, module_model, config):
        property_name = config['property_name'].split('/')[0]
        if property_name == 'Text':
            return self.parse_text_property(module_model, config)

        if property_name == 'Gap type':
            return self.parse_gap_type_property(module_model, config)

        if property_name == 'Value type':
            return self.parse_value_type_property(module_model, config)

        if property_name == 'Open external link in':
            return self.parse_open_in_new_tab_property(module_model, config)

        if property_name in self.TEXT_ATTRIBUTE_NAMES:
            return self.parse_attribute_property(module_model, config, False)

        if property_name in self.BOOLEAN_ATTRIBUTE_NAMES:
            return self.parse_attribute_property(module_model, config, True)

        if property_name == 'Speech Text':
            return self._parse_speech_text(module_model, config)

        raise NotImplementedError("That properties is not implemented yet!")

    def parse_text_property(self, module_model, config):
        text_element = module_model.get_element('text')
        new_value = config['new_value']

        self._change_cdata_property(text_element, new_value, 'text')
        return True

    def parse_gap_type_property(self, module_model, config):
        AVAILABLE_VALUES = ['editable', 'draggable', 'math']
        new_value = config['new_value'].lower()

        if new_value not in AVAILABLE_VALUES:
            self._non_valid_log('Value don\'t match to %s' % ", ".join(AVAILABLE_VALUES))
            return False

        text_element = module_model.get_element('text')

        self._change_property(text_element, str(new_value == 'draggable').lower(), 'draggable')
        self._change_property(text_element, str(new_value == 'math').lower(), 'math')

        return True

    def parse_value_type_property(self, module_model, config):
        AVAILABLE_TYPES = {
            'all': 'All',
            'number only': 'Number only',
            'letters only': 'Letters only',
            'alphanumeric': 'Alphanumeric'
        }
        new_value = config['new_value'].lower()

        if new_value not in AVAILABLE_TYPES:
            self._non_valid_log('Value don\'t match to "all", "number only", "letters only" or "alphanumeric"')
            return False

        text_element = module_model.get_element('text')
        return self._change_property(text_element, AVAILABLE_TYPES[new_value], 'valueType')

    def parse_open_in_new_tab_property(self, module_model, config):
        AVAILABLE_VALUES = {
            'new tab': 'true',
            'same tab': 'false'
        }

        new_value = config['new_value'].lower()

        if new_value not in AVAILABLE_VALUES:
            self._non_valid_log('Value don\'t match to "new tab" or "same tab"')
            return False

        text_element = module_model.get_element('text')
        return self._change_boolean_value(text_element, AVAILABLE_VALUES[new_value], 'openLinksinNewTab')

    def parse_attribute_property(self, module_model, config, is_boolean):
        new_value = config['new_value']
        attribute_name = self.TEXT_ATTRIBUTE_NAMES.get(config['property_name']) or self.BOOLEAN_ATTRIBUTE_NAMES.get(config['property_name'])
        if is_boolean:
            if new_value.lower() in ['true', 'false']:
                new_value = new_value.lower()
            else:
                self._non_valid_log('Value don\'t match to "true" or "false"')
                return False

        text_element = module_model.get_element('text')
        return self._change_property(text_element, new_value, attribute_name)



class CheckButtonModuleParser(ModuleModelParser, ModuleParser, SpeechTextModuleParser):
    TAG_NAME = "checkModule"
    SPEECH_TEXT_ELEMENT = 'button'

    SPEECH_TEXT_ITEM = [
        DefaultFrontEndPropertyModel('Selected'),
        DefaultFrontEndPropertyModel('Correct'),
        DefaultFrontEndPropertyModel('Wrong'),
        DefaultFrontEndPropertyModel('Percentage result'),
        DefaultFrontEndPropertyModel('Page edition is blocked'),
        DefaultFrontEndPropertyModel('Page edition is not blocked'),
    ]

    MODEL = [
        DefaultFrontEndPropertyModel('Check text'),
        DefaultFrontEndPropertyModel('unCheck text'),
        StaticListFrontEndPropertyModel(name='Speech Text', children=SPEECH_TEXT_ITEM),
    ]

    SPEECH_TEXT_ATTRIBUTE_NAMES = {
        'Selected': 'selected',
        'Correct': 'correct',
        'Wrong': 'wrong',
        'Percentage result': 'percentage_result',
        'Page edition is blocked': 'edit_block',
        'Page edition is not blocked': 'no_edit_block',
    }

    ATTRIBUTES_NAMES = {
        'Check text': 'checkTitle',
        'unCheck text': 'unCheckTitle'
    }

    def dispatch(self, module_model, config):
        property_name = config['property_name'].split('/')[0]
        if property_name in self.ATTRIBUTES_NAMES:
            button_element = module_model.get_element('button')
            new_value = config['new_value']
            attribute_name = self.ATTRIBUTES_NAMES[property_name]
            return self._change_property(button_element, new_value, attribute_name)

        if property_name == 'Speech Text':
            return self._parse_speech_text(module_model, config)

        raise NotImplementedError('Property not implemented yet!')


class CheckCounterModuleParser(EmptyModuleParser, ModuleModelParser):
    TAG_NAME = 'checkCounterModule'

    MODEL = [

    ]


class ChoiceModuleParser(ModuleModelParser, ModuleParser, SpeechTextModuleParser):
    TAG_NAME = 'choiceModule'
    SPEECH_TEXT_ELEMENT = 'choice'

    ITEM_CHILDREN = [
        DefaultFrontEndPropertyModel('Value'),
        DefaultFrontEndPropertyModel('Text'),
        DefaultFrontEndPropertyModel('Event')
    ]

    SPEECH_TEXT_ITEM = [
        DefaultFrontEndPropertyModel('Selected'),
        DefaultFrontEndPropertyModel('Deselected'),
        DefaultFrontEndPropertyModel('Correct'),
        DefaultFrontEndPropertyModel('Incorrect'),
    ]

    MODEL = [
        ListFrontEndPropertyModel(name='Item', children=ITEM_CHILDREN),
        DefaultFrontEndPropertyModel(name='Is multi'),
        DefaultFrontEndPropertyModel(name='Is disabled'),
        DefaultFrontEndPropertyModel(name='Is activity'),
        DefaultFrontEndPropertyModel(name='Random Order'),
        DefaultFrontEndPropertyModel(name='Horizontal Layout'),
        StaticListFrontEndPropertyModel(name='Speech text', children=SPEECH_TEXT_ITEM),
    ]

    CHOICE_ATTRIBUTES_NAMES = {
        'Is multi': 'isMulti',
        'Is disabled': 'isDisabled',
        'Is activity': 'isActivity',
        'Random Order': 'randomOrder',
        'Horizontal Layout': 'isHorizontal'
    }

    SPEECH_TEXT_ATTRIBUTE_NAMES = {
        'Selected': 'selected',
        'Deselected': 'deselected',
        'Correct': 'correct',
        'Incorrect': 'incorrect',
    }

    def dispatch(self, module_model, config):
        property_name = config['property_name'].split('/')[0]

        if property_name in self.CHOICE_ATTRIBUTES_NAMES:
            return self.__parse_choice_attribute(module_model, config)

        if property_name == 'Item':
            return self.__parse_list(module_model, config)

        if property_name == 'Speech text':
            return self._parse_speech_text(module_model, config)

    def __parse_choice_attribute(self, module_model, config):
        new_value = config['new_value'].lower()
        if new_value not in ['true', 'false']:
            self._non_valid_log('New value must be: "true" or "false"')
            return False

        attribute_name = self.CHOICE_ATTRIBUTES_NAMES[config['property_name']]
        choice = module_model.get_element('choice')
        self._change_property(choice, new_value, attribute_name)
        return True

    def __parse_list(self, module_model, config):
        property_name = config['property_name']
        path = property_name.split('/')
        if path[0] != 'Item':
            raise NotImplementedError('Property is not implemented yet!')

        options = module_model.get_element('options')
        is_changed = False
        for index, option in enumerate(options.childNodes):
            if number_in_regex_range(index + 1, config['list_row_number']):
                is_changed = self.__parse_option(option, config, index + 1) or is_changed

        return is_changed

    def __parse_option(self, option_xml, config, row_number):
        path = config['property_name'].split('/')
        current_property_name = path[-1]
        new_value = config['new_value']

        if current_property_name == 'Value':
            self._change_property(option_xml, config['new_value'], 'value', row_number)

        elif current_property_name == 'Text':
            text_element = option_xml.getElementsByTagName('text')[0]
            self._change_cdata_property(text_element, new_value, 'text')

        elif current_property_name == 'Event':
            feedback = option_xml.getElementsByTagName('feedback')[0]
            if feedback.firstChild is None:
                text_node = Document().createTextNode('')
                feedback.appendChild(text_node)

            self._change_log(feedback.firstChild.wholeText, new_value, 'text')
            feedback.firstChild.data = new_value
        else:
            raise NotImplementedError('Property not implemented yet!')

        return True


class ErrorCounterModuleParser(ModuleModelParser, ModuleParser):
    TAG_NAME = 'errorCounterModule'

    MODEL = [
        DefaultFrontEndPropertyModel('Show errors'),
        DefaultFrontEndPropertyModel('Show mistakes'),
        DefaultFrontEndPropertyModel('Calculate in real time')
    ]

    COUNTER_ATTRIBUTES_NAME = {
        "Show errors": "showErrorCounter",
        "Show mistakes": "showMistakeCounter",
        "Calculate in real time": "realTimeCalculation"
    }

    def dispatch(self, module_model, config):
        property_name = config['property_name']
        if property_name not in self.COUNTER_ATTRIBUTES_NAME:
            raise NotImplementedError('Property not implemented yet!')

        attribute_name = self.COUNTER_ATTRIBUTES_NAME[property_name]
        new_value = config['new_value'].lower()

        if new_value not in ['true', 'false']:
            self._non_valid_log('New value must be: "true" or "false"')
            return False

        counter = module_model.get_element('counter')

        return self._change_property(counter, new_value, attribute_name)


class ImageModuleParser(ModuleModelParser, ModuleParser):
    TAG_NAME = "imageModule"

    MODEL = [
        DefaultFrontEndPropertyModel('Image'),
        DefaultFrontEndPropertyModel('Mode'),
        DefaultFrontEndPropertyModel('Animated gif refresh')
    ]

    AVAILABLE_STRETCH_MODE = {
        "stretch": "stretch",
        "keepaspect": "keepAspect",
        "originalsize": "originalSize"
    }

    IMAGE_ATTRIBUTES_NAME = {
        'Image': 'src',
        'Mode': 'mode',
        'Animated gif refresh': 'animatedGifRefresh'
    }

    def dispatch(self, module_model, config):
        property_name = config['property_name']
        new_value = config['new_value']
        image = module_model.get_element('image')
        attribute_name = self.IMAGE_ATTRIBUTES_NAME[property_name]

        if property_name == 'Animated gif refresh':
            if new_value.lower() not in ['true', 'false']:
                self._non_valid_log('New value must be: "true" or "false"')
                return False

            return self._change_property(image, new_value.lower(), attribute_name)

        if property_name == 'Mode':
            if new_value.lower() not in self.AVAILABLE_STRETCH_MODE:
                self._non_valid_log('New value must be: "stretch", "keepAspect" or "originalSize"')
                return False

            return self._change_property(image, self.AVAILABLE_STRETCH_MODE[new_value.lower()], attribute_name)

        if property_name == 'Image':
            return self._change_property(image, new_value, attribute_name)

        raise NotImplementedError('Property not implemented yet!')


class ImageGapModuleParser(ModuleModelParser, ModuleParser, SpeechTextModuleParser):
    TAG_NAME = 'imageGapModule'

    SPEECH_TEXT_ELEMENT = 'gap'

    SPEECH_TEXT_ITEM = [
        DefaultFrontEndPropertyModel('Inserted'),
        DefaultFrontEndPropertyModel('Removed'),
        DefaultFrontEndPropertyModel('Correct'),
        DefaultFrontEndPropertyModel('Wrong'),
        DefaultFrontEndPropertyModel('Empty'),
    ]

    SPEECH_TEXT_ATTRIBUTE_NAMES = {
        'Inserted': 'insertedWCAG',
        'Removed': 'removedWCAG',
        'Correct': 'correctWCAG',
        'Wrong': 'wrongWCAG',
        'Empty': 'emptyWCAG'
    }

    MODEL = [
        DefaultFrontEndPropertyModel('Answer ID'),
        DefaultFrontEndPropertyModel('Is activity'),
        DefaultFrontEndPropertyModel('onCorrect'),
        DefaultFrontEndPropertyModel('onWrong'),
        DefaultFrontEndPropertyModel('onEmpty'),
        DefaultFrontEndPropertyModel('Is Disabled'),
        DefaultFrontEndPropertyModel('Block wrong answers'),
        StaticListFrontEndPropertyModel(name='Speech text', children=SPEECH_TEXT_ITEM),
    ]

    IMAGE_GAP_GAP_ATTRIBUTES_NAME = {
        'Answer ID': 'answerId',
        'Is activity': 'isActivity',
        'Is Disabled': 'isDisabled',
        'Block wrong answers': 'blockWrongAnswers'
    }

    IMAGE_GAP_EVENTS = ['onCorrect', 'onWrong', 'onEmpty']

    def dispatch(self, module_model, config):
        if config['property_name'] in self.IMAGE_GAP_GAP_ATTRIBUTES_NAME:
            return self.__change_gap_attributes(module_model, config)
        elif config['property_name'] in self.IMAGE_GAP_EVENTS:
            return self.__change_events_code(module_model, config)
        elif config['property_name'].split('/')[0] == 'Speech text':
            return self._parse_speech_text(module_model, config)

        raise NotImplementedError('Property not implemented yet!')

    def __change_gap_attributes(self, module_model, config):
        gap_element = module_model.get_element('gap')
        new_value = config['new_value']
        attribute_name = self.IMAGE_GAP_GAP_ATTRIBUTES_NAME[config['property_name']]

        if config['property_name'] == 'Answer ID':
            self._change_property(gap_element, new_value, attribute_name)
            return True

        return self._change_boolean_value(gap_element, new_value, attribute_name)

    def __change_events_code(self, module_model, config):
        attribute_name = config['property_name']
        events = module_model.get_element('events')
        new_value = config['new_value']

        for event in events.childNodes:
            if event.getAttribute('name') == attribute_name:
                return self._change_property(event, new_value, 'code')
        return False


class ImageSourceModuleParser(ModuleModelParser, ModuleParser, SpeechTextModuleParser):
    TAG_NAME = 'imageSourceModule'

    SPEECH_TEXT_ELEMENT = 'image'

    SPEECH_TEXT_ITEM = [
        DefaultFrontEndPropertyModel('Selected'),
        DefaultFrontEndPropertyModel('Deselected')
    ]

    SPEECH_TEXT_ATTRIBUTE_NAMES = {
        'Selected': 'selectedWCAG',
        'Deselected': 'deselectedWCAG'
    }

    MODEL = [
        DefaultFrontEndPropertyModel('Image'),
        DefaultFrontEndPropertyModel('Is Disabled'),
        DefaultFrontEndPropertyModel('Removable'),
        StaticListFrontEndPropertyModel(name='Speech text', children=SPEECH_TEXT_ITEM)
    ]

    IMAGE_SOURCE_ATTRIBUTES_NAMES = {
        'Image': 'src',
        'Is Disabled': 'isDisabled',
        'Removable': 'removable',
        'Speech text/Selected': 'selectedWCAG',
        'Speech text/Deselected': 'deselectedWCAG'
    }

    def dispatch(self, module_model, config):
        property_name = config['property_name']
        image = module_model.get_element('image')
        new_value = config['new_value']

        if property_name not in self.IMAGE_SOURCE_ATTRIBUTES_NAMES:
            raise NotImplementedError('Property not implemented yet!')

        attribute_name = self.IMAGE_SOURCE_ATTRIBUTES_NAMES[property_name]

        if property_name == 'Image':
            return self._change_property(image, new_value, attribute_name)

        if property_name.split('/')[0] == 'Speech text':
            return self._parse_speech_text(module_model, config)

        return self._change_boolean_value(image, new_value, attribute_name)


class LessonResetModuleParser(ModuleModelParser, ModuleParser):
    TAG_NAME = 'lessonResetModule'

    MODEL = [
        DefaultFrontEndPropertyModel('Title'),
        DefaultFrontEndPropertyModel('Reset mistakes'),
        DefaultFrontEndPropertyModel('Reset checks')
    ]

    LESSON_RESET_ATTRIBUTES_NAMES = {
        'Title': 'title',
        'Reset mistakes': 'resetMistakes',
        'Reset checks': 'resetChecks'
    }

    def dispatch(self, module_model, config):
        property_name = config['property_name']
        lesson_reset = module_model.get_element('lessonReset')
        new_value = config['new_value']

        if property_name in self.LESSON_RESET_ATTRIBUTES_NAMES:
            attribute_name = self.LESSON_RESET_ATTRIBUTES_NAMES[property_name]
            if property_name == 'Title':
                return self._change_property(lesson_reset, new_value, attribute_name)

            return self._change_boolean_value(lesson_reset, new_value, attribute_name)


class LimitedCheckModuleParser(ModuleModelParser, ModuleParser):
    TAG_NAME = 'limitedCheckModule'

    MODEL = [
        DefaultFrontEndPropertyModel('Check text'),
        DefaultFrontEndPropertyModel('Uncheck text'),
        DefaultFrontEndPropertyModel('Works with')
    ]

    LIMITED_CHECK_ATTRIBUTES_NAMES = {
        'Check text': 'checkText',
        'Uncheck text': 'unCheckText'
    }

    def dispatch(self, module_model, config):
        property_name = config['property_name']
        new_value = config['new_value']
        limited_check = module_model.get_element('limitedCheck')

        if property_name in self.LIMITED_CHECK_ATTRIBUTES_NAMES:
            attribute_name = self.LIMITED_CHECK_ATTRIBUTES_NAMES[property_name]
            return self._change_property(limited_check, new_value, attribute_name)

        if property_name == 'Works with':
            return self._change_cdata_property(limited_check, new_value, 'worksWith')


class LimitedResetModuleParser(ModuleModelParser, ModuleParser):
    TAG_NAME = 'limitedResetModule'
    MODEL = [
        DefaultFrontEndPropertyModel('Title'),
        DefaultFrontEndPropertyModel('Works with')
    ]

    def dispatch(self, module_model, config):
        property_name = config['property_name']
        new_value = config['new_value']
        limited_reset = module_model.get_element('limitedReset')

        if property_name == 'Title':
            return self._change_property(limited_reset, new_value, 'title')

        if property_name == 'Works with':
            return self._change_cdata_property(limited_reset, new_value, 'worksWith')

        raise NotImplementedError('Property not implemented yet!')


class OrderingModuleParser(ModuleModelParser, ModuleParser, SpeechTextModuleParser):
    TAG_NAME = 'orderingModule'
    SPEECH_TEXT_ELEMENT = 'ordering'

    ORDERING_LIST_MODEL = [
        DefaultFrontEndPropertyModel('Text')
    ]

    SPEECH_TEXT_ITEM = [
        DefaultFrontEndPropertyModel('Selected'),
        DefaultFrontEndPropertyModel('Deselected'),
        DefaultFrontEndPropertyModel('Replaced with'),
        DefaultFrontEndPropertyModel('Correct'),
        DefaultFrontEndPropertyModel('Wrong'),
    ]

    MODEL = [
        DefaultFrontEndPropertyModel('Is Vertical'),
        ListFrontEndPropertyModel(name='Ordering item', children=ORDERING_LIST_MODEL),
        DefaultFrontEndPropertyModel('Order'),
        DefaultFrontEndPropertyModel('Is activity'),
        DefaultFrontEndPropertyModel('Event with for all elements'),
        DefaultFrontEndPropertyModel('Gradually score'),
        StaticListFrontEndPropertyModel(name='Speech text', children=SPEECH_TEXT_ITEM),
    ]

    SPEECH_TEXT_ATTRIBUTE_NAMES = {
        'Selected': 'selected',
        'Deselected': 'deselected',
        'Replaced with': 'replaced_with',
        'Correct': 'correct',
        'Wrong': 'wrong',
    }

    ORDERING_LIST_ATTRIBUTES_NAMES = {
        'Is Vertical': 'isVertical',
        'Order': 'optionalOrder',
        'Is activity': 'isActivity',
        'Event with for all elements': 'allElementsHasSameWidth',
        'Gradually score': 'graduallyScore'
    }

    def dispatch(self, module_model, config):
        property_name = config['property_name'].split('/')[0]

        if property_name == 'Ordering item':
            return self.__change_list_elements(module_model, config)

        if property_name in self.ORDERING_LIST_ATTRIBUTES_NAMES:
            return self.__change_attribute(module_model, config)

        if property_name == 'Speech text':
            return self._parse_speech_text(module_model, config)

        raise NotImplementedError('Property not implemented yet!')

    def __change_list_elements(self, module_model, config):
        items = module_model.get_all_elements('item')
        changed = False
        for index, item in enumerate(items):
            if number_in_regex_range(index + 1, config['list_row_number']):
                changed = self.__change_row_element(item, config, index + 1) or changed

        return changed

    def __change_row_element(self, row, config, row_number):
        new_value = config['new_value']
        self._change_cdata_property(row, new_value, 'row', row_number=row_number)
        return True

    def __change_attribute(self, module_model, config):
        property_name = config['property_name']
        attribute_name = self.ORDERING_LIST_ATTRIBUTES_NAMES[property_name]
        ordering = module_model.get_element('ordering')
        new_value = config['new_value']

        if property_name == 'Order':
            return self._change_property(ordering, new_value, attribute_name)

        return self._change_boolean_value(ordering, new_value, attribute_name)


class PageProgressModuleParser(ModuleModelParser, EmptyModuleParser):
    TAG_NAME = 'pageProgressModule'
    MODEL = []


class ReportModuleParser(ModuleModelParser, ModuleParser):
    TAG_NAME = 'reportModule'

    MODEL = [
        DefaultFrontEndPropertyModel('Errors label'),
        DefaultFrontEndPropertyModel('Checks label'),
        DefaultFrontEndPropertyModel('Result label'),
        DefaultFrontEndPropertyModel('Total label'),
        DefaultFrontEndPropertyModel('Show counters'),
        DefaultFrontEndPropertyModel('Title width')
    ]

    REPORT_MODULE_LABELS_ATTRIBUTES_NAMES = {
        'Show counters': 'showCounters',
        'Title width': 'pageNameWidth'
    }

    REPORT_MODULE_LABEL_NAMES = {
        'Errors label': 'ErrorCount',
        'Checks label': 'CheckCount',
        'Result label': 'Results',
        'Total label': 'Total'
    }

    def dispatch(self, module_model, config):
        property_name = config['property_name']
        if property_name in self.REPORT_MODULE_LABELS_ATTRIBUTES_NAMES:
            return self.__change_labels(module_model, config)

        if property_name in self.REPORT_MODULE_LABEL_NAMES:
            return self.__change_label(module_model, config)

    def __change_labels(self, module_model, config):
        labels = module_model.get_element('labels')
        property_name = config['property_name']
        attribute_name = self.REPORT_MODULE_LABELS_ATTRIBUTES_NAMES[property_name]
        new_value = config['new_value']

        if property_name == 'Show counters':
            return self._change_boolean_value(labels, new_value, attribute_name)
        return self._change_property(labels, new_value, attribute_name)

    def __change_label(self, module_model, config):
        property_name = config['property_name']
        new_value = config['new_value']
        labels_elements = module_model.get_all_elements('label')
        label_name = self.REPORT_MODULE_LABEL_NAMES[property_name]

        for label in labels_elements:
            if label.getAttribute('name') == label_name:
                return self._change_property(label, new_value, 'value')

        raise NotImplementedError('Property not implemented yet!')


class ShapeModuleParser(ModuleModelParser, EmptyModuleParser):
    TAG_NAME = 'shapeModule'
    MODEL = []


class SourceListModuleParser(ModuleModelParser, ModuleParser, SpeechTextModuleParser):
    TAG_NAME = 'sourceListModule'
    SPEECH_TEXT_ELEMENT = 'items'
    LIST_MODEL = [
        DefaultFrontEndPropertyModel('Name')
    ]

    SPEECH_TEXT_ITEM = [
        DefaultFrontEndPropertyModel('Selected'),
        DefaultFrontEndPropertyModel('Deselected'),
    ]

    MODEL = [
        ListFrontEndPropertyModel('Items', children=LIST_MODEL),
        DefaultFrontEndPropertyModel('Removable'),
        DefaultFrontEndPropertyModel('Vertical'),
        DefaultFrontEndPropertyModel('Random order'),
        StaticListFrontEndPropertyModel(name='Speech text', children=SPEECH_TEXT_ITEM),
    ]

    SPEECH_TEXT_ATTRIBUTE_NAMES = {
        'Selected': 'selected',
        'Deselected': 'deselected',
    }

    SOURCE_LIST_ITEMS_ATTRIBUTES_NAMES = {
        'Random order': 'randomOrder',
        'Removable': 'removable',
        'Vertical': 'vertical'
    }

    def dispatch(self, module_model, config):
        property_name = config['property_name'].split('/')[0]
        if property_name == 'Items':
            return self.__change_items(module_model, config)

        if property_name in self.SOURCE_LIST_ITEMS_ATTRIBUTES_NAMES:
            return self.__change_attribute(module_model, config)

        if property_name == 'Speech text':
            return self._parse_speech_text(module_model, config)

        raise NotImplementedError('Property not implemented yet!')

    def __change_items(self, module_model, config):
        rows = module_model.get_all_elements('item')
        changed = False
        for index, row in enumerate(rows):
            changed = self.__change_row(row, config, index) or changed

        return changed

    def __change_row(self, row, config, index):
        if number_in_regex_range(index + 1, config['list_row_number']):
            new_value = config['new_value']
            self._change_cdata_property(row, new_value, 'Name', row_number=index+1)
            return True
        return False

    def __change_attribute(self, module_model, config):
        items = module_model.get_element('items')
        new_value = config['new_value']
        property_name = config['property_name'].split('/')[0]
        attribute_name = self.SOURCE_LIST_ITEMS_ATTRIBUTES_NAMES[property_name]

        return self._change_boolean_value(items, new_value, attribute_name)



class ButtonModuleParser(ModuleParser, SpeechTextModuleParser):
    TAG_NAME = 'buttonModule'
    BUTTON_NAME = 'init'
    BOOLEAN_ATTRIBUTES = {}
    TEXT_ATTRIBUTES = {}
    SPEECH_TEXT_ATTRIBUTE_NAMES = {}
    SPEECH_TEXT_ELEMENT = 'button'

    def dispatch(self, module_model, config):
        new_value = config['new_value']
        property_name = config['property_name']
        button_element = module_model.get_element('button')
        attribute_name = self.BOOLEAN_ATTRIBUTES.get(property_name) or self.TEXT_ATTRIBUTES.get(property_name)

        if self.BUTTON_NAME == button_element.getAttribute('type'):
            if property_name in self.BOOLEAN_ATTRIBUTES:
                return self._change_boolean_value(button_element, new_value, attribute_name)
            elif property_name in self.TEXT_ATTRIBUTES:
                return self._change_property(button_element, new_value, attribute_name)

            elif property_name.split('/')[0] == 'Speech text':
                return self._parse_speech_text(module_model, config)

            raise NotImplementedError('Property not implemented yet!')


class NextPageButtonModuleParser(ModuleModelParser, ButtonModuleParser):
    MODEL = [
        DefaultFrontEndPropertyModel('Title')
    ]

    BUTTON_NAME = 'nextPage'

    BOOLEAN_ATTRIBUTES = {}
    TEXT_ATTRIBUTES = {
        'Title': 'text'
    }


class PrevPageButtonModuleParser(NextPageButtonModuleParser):
    BUTTON_NAME = 'prevPage'


class ResetButtonModuleParser(ModuleModelParser, ButtonModuleParser):
    BUTTON_NAME = 'reset'

    SPEECH_TEXT_ITEM = [
        DefaultFrontEndPropertyModel('Page has been reset'),
    ]

    MODEL = [
        DefaultFrontEndPropertyModel('Title'),
        DefaultFrontEndPropertyModel('Confirm reset'),
        DefaultFrontEndPropertyModel('Confirmation info'),
        DefaultFrontEndPropertyModel('Confirmation yes text'),
        DefaultFrontEndPropertyModel('Confirmation no text'),
        StaticListFrontEndPropertyModel(name='Speech text', children=SPEECH_TEXT_ITEM),
    ]

    BOOLEAN_ATTRIBUTES = {
        'Confirm reset': 'confirmReset'
    }

    SPEECH_TEXT_ATTRIBUTE_NAMES = {
        'Page has been reset': 'resetReset',
    }

    TEXT_ATTRIBUTES = {
        'Title': 'text',
        'Confirmation info': 'confirmInfo',
        'Confirmation yes text': 'confirmYesInfo',
        'Confirmation no text': 'confirmNoInfo'
    }


class CancelButtonModuleParser(NextPageButtonModuleParser):
    BUTTON_NAME = 'cancel'

    MODEL = [
        DefaultFrontEndPropertyModel('Title')
    ]


class PopupButtonModuleParser(ModuleModelParser, ButtonModuleParser):
    BUTTON_NAME = 'popup'

    MODEL = [
        DefaultFrontEndPropertyModel('Title'),
        DefaultFrontEndPropertyModel('Page'),
        DefaultFrontEndPropertyModel('Additional classes'),
        DefaultFrontEndPropertyModel('Popup top position'),
        DefaultFrontEndPropertyModel('Popup left position')
    ]

    TEXT_ATTRIBUTES = {
        'Title': 'text',
        'Page': 'onclick',
        'Additional classes': 'additionalClasses',
        'Popup top position': 'popupTopPosition',
        'Popup left position': 'popupLeftPosition'
    }


class GoToPageButtonModuleParser(ModuleModelParser, ButtonModuleParser):
    BUTTON_NAME = 'gotoPage'

    MODEL = [
        DefaultFrontEndPropertyModel('Title'),
        DefaultFrontEndPropertyModel('Page'),
        DefaultFrontEndPropertyModel('Page index')
    ]

    TEXT_ATTRIBUTES = {
        'Title': 'text',
        'Page': 'onclick',
        'Page index': 'pageIndex'
    }


# This factory should return parser for addon or module (one parser for addons and N parsers for N modules)
# noinspection PyMethodMayBeStatic
ModuleParserFactory = {
        "Check Button": CheckButtonModuleParser,
        "Check Counter": CheckCounterModuleParser,
        "Choice": ChoiceModuleParser,
        "ErrorCounter": ErrorCounterModuleParser,
        "Image": ImageModuleParser,
        "Image gap": ImageGapModuleParser,
        "Image source": ImageSourceModuleParser,
        "Lesson Reset": LessonResetModuleParser,
        "Limited Check": LimitedCheckModuleParser,
        "Limited Reset": LimitedResetModuleParser,
        "Ordering": OrderingModuleParser,
        "Page Progress": PageProgressModuleParser,
        "Report": ReportModuleParser,
        "Shape": ShapeModuleParser,
        "Source list": SourceListModuleParser,
        "Text": TextModuleParser,
        "nextPageButton": NextPageButtonModuleParser,
        "prevPageButton": PrevPageButtonModuleParser,
        "resetButton": ResetButtonModuleParser,
        "cancelButton": CancelButtonModuleParser,
        "popupButton": PopupButtonModuleParser,
        "gotoPageButton": GoToPageButtonModuleParser
}
