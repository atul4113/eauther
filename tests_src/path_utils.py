"""
    Mixin Classes for Manipulation for paths to use in tests
    GetPathMixin - resolutes path to a file
    LoadXMLSFromFiles - loads from file a xml and retursn etree args or kwargs
"""

from lxml import etree
from os.path import dirname, abspath, join, normpath, realpath, abspath


class GetPathMixin(object):

    def get_path(self, *args):
        TEST_DIR = (dirname(abspath(__file__)))
        return join(TEST_DIR, *args)


class LoadXMLsFromFiles(object):

    def __get_etree_element(self, *args):
        with open(self.get_path(*args), "r") as f:
            return etree.parse(f)

    def load_xmls(self, *args, **kwargs):
        """
            args: iterable of sequences for path to xml file
            kwargs: values are sequences for path to xml file

            for args, returns list of etree elements
            for kwargs returns dictionary of key: etree element
        """

        result_args_xmls = []
        results_kwargs_xmls = {}
        for paths in args:
            el = self.__get_etree_element(*paths)
            result_args_xmls.append(el)

        for key, value in kwargs.items():
            results_kwargs_xmls[key] = self.__get_etree_element(value)

        return result_args_xmls, results_kwargs_xmls

    def load_xml_from_string(self, data):
        """
        :param data: string
        """
        return etree.fromstring(data)


class LoadFileMixin(object):

    def load_file(self, *args, **kwargs):
        with open(self.get_path(*args), "r") as f:
            return f.read()

    def get_file_object(self, *args):
        return open(self.get_path(*args), "r")