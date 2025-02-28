import csv
import re
from xml.dom import Node
from src.lorepo.mycontent.models import Content, FileStorage
from src.libraries.utility.helpers import get_object_or_none
from django.shortcuts import get_object_or_404
from src.mauthor.localization.IcplayerZipped import IcplayerZipped
from xml.dom import minidom


class Logger(object):

    FIELD_NAMES = ["type", "action", "title", "property_name", "row_number", "old_value", "new_value", "version_number", "lesson_id", "page_id", "addon_id", "module_id", "is_common", "page_number", "element_type", "message", "user_values"]

    def __init__(self, json, gcs_file):
        self.csv_writer = csv.DictWriter(gcs_file, fieldnames=Logger.FIELD_NAMES)
        self.add_log(user_values=json)
        self.csv_writer.writeheader()

    def add_log(self, **kwargs):
        if self.csv_writer is None:
            raise Exception("Logger don't have csv writter")
        log = {}
        for key, value in list(kwargs.items()):
            if isinstance(value, str):
                log[key] = value.encode('utf-8')
            else:
                log[key] = value
        self.csv_writer.writerow(log)


class NodesIterator(object):
    def __init__(self, child_nodes):
        self.__nodes = child_nodes
        self.__actual_index = -1

    def __iter__(self):
        return self

    def __next__(self):
        while True:
            if self.__actual_index + 1 == len(self.__nodes):
                raise StopIteration
            self.__actual_index += 1
            if self.__nodes[self.__actual_index].nodeType == Node.ELEMENT_NODE:
                return self.__nodes[self.__actual_index]


def get_property_by_name(xml, property_name):
    for property in NodesIterator(xml.childNodes):
        if property.getAttribute('name') == property_name:
            return property

    return None


def get_element_by_tag_name(xml, tag_name):
    for tag in NodesIterator(xml.childNodes):
        if tag.tagName == tag_name:
            return tag
    return None


def get_items_tag(xml):
    for tag in NodesIterator(xml.childNodes):
        if tag.tagName == 'items':
            return tag
    return None


def number_in_regex_range(number, regex):
    match = re.match("^\[(\d+|start)-(\d+|end)]$", regex)
    if match:
        from_value = match.group(1)
        to_value = match.group(2)
        if from_value == 'start':
            from_value = 1
        if to_value == 'end':
            to_value = float('Inf')

        return int(from_value) <= number <= float(to_value)

    values = [int(value) for value in regex.split(',')]

    if number in values:
        return True

    return False


def get_addon_model(name):
    with IcplayerZipped() as player:
        if name in player.get_addons_list():
            return player.get_model(name)
        else:
            return get_private_addon_model(name)


def get_private_addon_model(name):
    content = get_object_or_404(Content, name=name, content_type=3)
    file_id = content.file.id
    descriptor = minidom.parseString(get_object_or_none(FileStorage, id=file_id).contents)
    return descriptor.getElementsByTagName('model')[0]
