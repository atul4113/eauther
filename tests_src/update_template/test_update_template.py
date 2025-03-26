from deepdiff import DeepDiff

from .base_update_template_testing_class import BaseUpdateTemplateMixin


class TestThemeV0(BaseUpdateTemplateMixin):
    folder = "themeV0"
    template_pk = 6485362123997184

    def test_update_templateV0_have_to_override_default_layout_styles(self):
        content_name = "contentV2.xml"
        theme_name = "themeV0.xml"
        expected_result_name = "resultV2.xml"

        result, expected_result = self.perform_test(content_name=content_name, theme_name=theme_name, expected_name=expected_result_name)
        assert DeepDiff(expected_result, result, ignore_order=True) == {}


class TestMissingLayouts(BaseUpdateTemplateMixin):
    folder = "missingLayouts"
    template_pk = 6485362123997184

    def test_update_template_missing_layouts_from_template_have_to_be_copied_content_v0(self):
        content_name = "contentV0.xml"
        theme_name = "themeV2.xml"
        expected_result_name = "resultV2FromV0.xml"

        result, expected_result = self.perform_test(content_name=content_name, theme_name=theme_name,
                                                    expected_name=expected_result_name)
        assert DeepDiff(expected_result, result, ignore_order=True) == {}

    def test_update_template_missing_layouts_from_template_have_to_be_copied_content_v2_and_addon_descriptors(self):
        content_name = "contentV2MissingSomeAddonDescriptors.xml"
        theme_name = "themeV2.xml"
        expected_result_name = "resultV2.xml"

        result, expected_result = self.perform_test(content_name=content_name, theme_name=theme_name,
                                                    expected_name=expected_result_name)
        assert DeepDiff(expected_result, result, ignore_order=True) == {}

    def test_update_template_missing_layouts_from_template_have_to_be_copied_content_v2(self):
        content_name = "contentV2MissingSomeLayouts.xml"
        theme_name = "themeV2.xml"
        expected_result_name = "resultV2.xml"

        result, expected_result = self.perform_test(content_name=content_name, theme_name=theme_name,
                                                    expected_name=expected_result_name)
        assert DeepDiff(expected_result, result, ignore_order=True) == {}


class TestMissingAndDifferentAttributes(BaseUpdateTemplateMixin):
    folder = "missingAndDifferentAttributes"
    template_pk = 6485362123997184

    def test_update_template_missing_and_different_attributes_v2(self):
        content_name = "contentV2.xml"
        theme_name = "themeV2.xml"
        expected_result_name = "resultV2.xml"

        result, expected_result = self.perform_test(content_name=content_name, theme_name=theme_name,
                                                    expected_name=expected_result_name)
        assert DeepDiff(expected_result, result, ignore_order=True) == {}


class TestDifferentThresholds(BaseUpdateTemplateMixin):
    folder = "differentThresholds"
    template_pk = 6485362123997184

    def test_update_template_override_styles_when_names_match(self):
        content_name = "contentV2.xml"
        theme_name = "themeV2.xml"
        expected_result_name = "resultV2.xml"

        result, expected_result = self.perform_test(content_name=content_name, theme_name=theme_name,
                                                    expected_name=expected_result_name)
        assert DeepDiff(expected_result, result, ignore_order=True) == {}


class TestDifferentNames(BaseUpdateTemplateMixin):
    folder = "differentNames"
    template_pk = 6485362123997184

    def test_update_template_override_styles_when_thresholds_match(self):
        content_name = "contentV2.xml"
        theme_name = "themeV2.xml"
        expected_result_name = "resultV2.xml"

        result, expected_result = self.perform_test(content_name=content_name, theme_name=theme_name,
                                                    expected_name=expected_result_name)
        assert DeepDiff(expected_result, result, ignore_order=True) == {}


class TestDefaultDifferentNamesAndThresholds(BaseUpdateTemplateMixin):
    folder = "defaultDifferentNamesAndThresholds"
    template_pk = 6485362123997184

    def test_update_template_override_default_layouts_styles(self):
        content_name = "contentV2Default.xml"
        theme_name = "themeV2.xml"
        expected_result_name = "resultV2Default.xml"

        result, expected_result = self.perform_test(content_name=content_name, theme_name=theme_name,
                                                    expected_name=expected_result_name)
        assert DeepDiff(expected_result, result, ignore_order=True) == {}


class TestAddingLayoutsThresholdsOverlapping(BaseUpdateTemplateMixin):
    folder = "addingLayoutsThresholdsOverlapping"
    template_pk = 6485362123997184

    def test_update_template_adding_layout_with_overlapping_threshold(self):
        content_name = "contentV2.xml"
        theme_name = "themeV2.xml"
        expected_result_name = "resultV2.xml"

        result, expected_result = self.perform_test(content_name=content_name, theme_name=theme_name,
                                                    expected_name=expected_result_name)

        assert DeepDiff(expected_result, result, ignore_order=True) == {}