import zipfile
from xml.dom import minidom

from src.libraries.utility.urlfetch import fetch
from src.mauthor.localization.utils import filter_localization_properties
from .modules_list import MODULES_LIST
import src.settings as settings
import re

class IcplayerZipped(object):
    def __init__(self):
        self.ZIP_FILE_PATH = 'lorepo/templates/exchange/icplayer.zip'
        self.icplayer_file = None
        self.icplayer_file_list = None

    def __enter__(self):
        self.icplayer_file = zipfile.ZipFile(self.ZIP_FILE_PATH, 'r')
        self.icplayer_file_list = self.icplayer_file.namelist()

        return self

    def __exit__(self, type, value, traceback):
        self.icplayer_file.close()

    def _is_path_in_name_list(self, path):
        return self.icplayer_file_list.count(path) == 0

    def _get_addon_path_to_xml(self, addon_name):
        return "icplayer/addons/{0}.xml".format(addon_name)

    def _is_addon_custom(self, addon_name):
        addon_xml_path = self._get_addon_path_to_xml(addon_name)

        return self._is_path_in_name_list(addon_xml_path)

    def _get_addon_properties_from_xml(self, addon_name):
        data = self.icplayer_file.read(self._get_addon_path_to_xml(addon_name))

        desc_xml = minidom.parseString(data)
        properties = desc_xml.getElementsByTagName('property')

        return filter_localization_properties(properties)

    def _get_addon_properties_from_url(self, url_attribute):
        data = fetch('%s%s' % (settings.BASE_URL, url_attribute))
        if data:
            desc_xml = minidom.parseString(data)
            properties = desc_xml.getElementsByTagName('property')
            return filter_localization_properties(properties)

    def get_addon_properties(self, addon_name, url_attribute):
        if self._is_addon_custom(addon_name):
            properties = self._get_addon_properties_from_url(url_attribute)
        else:
            properties = self._get_addon_properties_from_xml(addon_name)

        return properties

    # noinspection SpellCheckingInspection
    def get_addons_list(self):
        addons = []
        for file in self.icplayer_file_list:
            # find all files with path icplayer/addons/*.xml
            match = re.match(r"icplayer/addons/([^/]+)(.xml)", file)
            if match:
                addons.append(match.group(1))
        return addons

    def get_modules_and_addons_list(self):
        return IcplayerZipped.get_modules_list() + self.get_addons_list()

    def get_model(self, addon_name):
        if addon_name in self.get_addons_list():
            data = self.icplayer_file.read(self._get_addon_path_to_xml(addon_name))
            xml = minidom.parseString(data)
            return xml.getElementsByTagName('model')[0]

    @staticmethod
    def get_modules_list():
        return MODULES_LIST

    def is_player_addon(self, addon_name):
        return self._get_addon_path_to_xml(addon_name) in self.icplayer_file_list
