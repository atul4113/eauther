from os.path import dirname, abspath, join

from lorepo.mycontent.lesson.update_content_template_task import UpdateContentBasingOnTemplate
from lxml import etree

from tests_src.xml_utils import etree_to_dict

TEST_DIR = (dirname(abspath(__file__)))


class PREFERENCES:
    USE_GRID = u'useGrid'
    GRID_SIZE = u'gridSize'
    STATIC_HEADER = u'staticHeader'
    STATIC_FOOTER = u'staticFooter'


class BaseUpdateTemplateMixin(object):
    test_folder = "testdata"
    folder = ""
    template_pk = 6485362123997184
    preferences = []

    def get_path(self, content_name, theme_name, expected_name):
        content_path = join(TEST_DIR, self.test_folder, self.folder, content_name)
        theme_path = join(TEST_DIR, self.test_folder, self.folder, theme_name)
        expected_path = join(TEST_DIR, self.test_folder, self.folder, expected_name)
        return content_path, theme_path, expected_path

    def perform_test(self, content_name="", theme_name="", expected_name="", preferences=None):
        content_path, theme_path, expected_result_path = self.get_path(content_name, theme_name, expected_name)

        with open(content_path, "r") as f, open(theme_path, "r") as f2, open(expected_result_path, "r") as expected_result_f:
            content_xml = f.read()
            theme_xml = f2.read()


            task = UpdateContentBasingOnTemplate(content_xml, theme_xml,
                                                 preferences if preferences is not None else self.preferences,
                                                 6485362123997184)
            changed, result_xml = task.execute()
            expected_xml = etree.fromstring(expected_result_f.read())

            result = etree_to_dict(result_xml)
            expected_result = etree_to_dict(expected_xml)

            return result, expected_result