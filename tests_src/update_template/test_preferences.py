from deepdiff import DeepDiff

from base_update_template_testing_class import BaseUpdateTemplateMixin


class TestPropagatePreferences(BaseUpdateTemplateMixin):
    folder = "preferences"
    preferences = [u'useGrid',
                   u'gridSize',
                   u'staticHeader',
                   u'staticFooter']

    def test_propagading_all_preferences(self):
        content_name = "contentV2.xml"
        theme_name = "themeV0.xml"
        expected_result_name = "resultV2.xml"

        result, expected_result = self.perform_test(content_name=content_name, theme_name=theme_name, expected_name=expected_result_name)

        assert DeepDiff(expected_result, result, ignore_order=True) == {}



    def test_propagading_none_preferences(self):
        content_name = "contentV2.xml"
        theme_name = "themeV0.xml"
        expected_result_name = "resultV2NoPreferences.xml"

        result, expected_result = self.perform_test(content_name=content_name, theme_name=theme_name, expected_name=expected_result_name, preferences=[])

        assert DeepDiff(expected_result, result, ignore_order=True) == {}