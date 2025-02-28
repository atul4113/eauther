import itertools
from collections import namedtuple

from src.libraries.utility.lxml_utilities.content.content_xml import AddonDescriptor, STYLE_ITEM, LAYOUT_ITEM
from src.libraries.utility.lxml_utilities.content.xml_model import ContentXML
from src.libraries.utility.lxml_utilities.utilities import ensure_subelement_exists, parse_main_xml_layouts
from lxml import etree


class UpdateContentBasingOnTemplate(object):

    TEMPLATE_KEY = "theme.href"
    DEFAULT_ID = "default"

    matching_layout = namedtuple("MatchingLayout", "match, layout_id")

    def __init__(self, content_main_xml_string, template_contents_xml_string, preferences, template_pk):
        self.main_content = ContentXML.fromstring(content_main_xml_string)
        self.template_content_root = etree.fromstring(template_contents_xml_string)
        self.preferences = preferences
        self.template_pk = template_pk

    def execute(self):
        ensure_subelement_exists(self.main_content.content_root, "metadata")
        ensure_subelement_exists(self.main_content.content_root, "addons")
        self.__set_content_template()
        self.__propagate_preferences()
        self.__update_content_addon_descriptors()
        self.__update_content_styles_by_template_settings()
        self.main_content.update_content_version()

        return True, self.main_content.content_root

    def __propagate_preferences(self):
        if len(self.preferences) > 0:
            template_entries = [entry for entry in self.template_content_root.iterfind(".//entry") if entry.get("key").decode("ascii") in self.preferences]

            content_metadata = self.main_content.content_root.find("metadata")
            for entry in template_entries:
                template_entry_key = entry.get("key")
                template_entry_value = entry.get("value")

                content_entry = content_metadata.find("entry[@key='{0}']".format(template_entry_key))
                if content_entry is None:
                    content_entry = etree.SubElement(content_metadata, "entry")

                content_entry.set("key", template_entry_key)
                content_entry.set("value", template_entry_value)

    def __set_content_template(self):
        metadata = self.main_content.content_root.find("metadata")
        template_entry = self.main_content.content_root.find(".//entry[@key='{0}']".format(self.TEMPLATE_KEY))

        if template_entry is None:
            template_entry = etree.SubElement(metadata, "entry")

        template_entry.set("key", self.TEMPLATE_KEY)
        template_entry.set("value", "/file/{0}".format(str(self.template_pk)))

    def __update_content_addon_descriptors(self):
        content_descriptors = { AddonDescriptor(addonId=descriptor.get("addonId"), href=descriptor.get("href")) for descriptor in self.main_content.content_root.iterfind(".//addon-descriptor")}
        template_descriptors = { AddonDescriptor(addonId=descriptor.get("addonId"), href=descriptor.get("href")) for descriptor in self.template_content_root.iterfind(".//addon-descriptor")}

        existing_ids = {descriptor.addonId for descriptor in content_descriptors}

        addon_descriptors = template_descriptors - content_descriptors

        content_addons = self.main_content.content_root.find("addons")
        addons_id_not_adeed_to_content = [desc for desc in addon_descriptors if desc.addonId not in existing_ids]
        for addonID, href in addons_id_not_adeed_to_content:
            addon_descriptor_entry = etree.SubElement(content_addons, "addon-descriptor")
            addon_descriptor_entry.set("addonId", addonID)
            addon_descriptor_entry.set("href", href)

    def __update_content_styles_by_template_settings(self):
        parsed_template_layouts = parse_main_xml_layouts(self.template_content_root)
        parsed_content_layouts = parse_main_xml_layouts(self.main_content.content_root)

        layouts_to_copy = []

        self.__override_default_layout_styles(parsed_template_layouts, parsed_content_layouts)

        for theme_layout_id, theme_layout in list(parsed_template_layouts.layouts.items()):
            if theme_layout.is_default:
                continue

            match = self.__match_any_layout(theme_layout, parsed_content_layouts.layouts)
            if match.match:
                theme_style = parsed_template_layouts[(STYLE_ITEM, theme_layout.styleid)]
                matching_layout = parsed_content_layouts[(LAYOUT_ITEM, match.layout_id)]
                overrided_matching_layout = matching_layout._replace(threshold=theme_layout.threshold)
                content_style = parsed_content_layouts[(STYLE_ITEM, overrided_matching_layout.styleid)]
                content_style = content_style._replace(css=theme_style.css)

                parsed_content_layouts[(STYLE_ITEM, content_style.id)] = content_style
                parsed_content_layouts[(LAYOUT_ITEM, overrided_matching_layout.id)] = overrided_matching_layout
            else:
                layouts_to_copy.append(theme_layout_id)

        self.__add_missing_layouts(layouts_to_copy, parsed_template_layouts, parsed_content_layouts)
        self.main_content.update_content_xml_with_layouts_and_css(parsed_content_layouts)

    def __override_default_layout_styles(self, parsed_template_layouts, parsed_content_layouts):
        default_theme_layout, default_theme_css_style = parsed_template_layouts.default_layout_style
        default_content_layout, default_content_css_style = parsed_content_layouts.default_layout_style

        default_content_layout = default_content_layout._replace(threshold=default_theme_layout.threshold)
        default_content_css_style = default_content_css_style._replace(css=default_theme_css_style.css)

        parsed_content_layouts[(LAYOUT_ITEM, default_content_layout.id)] = default_content_layout
        parsed_content_layouts[(STYLE_ITEM, default_content_css_style.id)] = default_content_css_style


    def __add_missing_layouts(self, layouts_to_copy, parsed_template_layouts, parsed_content_layouts):
        existing_thresholds = parsed_content_layouts.thresholds_set()

        for layout_id in layouts_to_copy:
            template_layout = parsed_template_layouts[(LAYOUT_ITEM, layout_id)]
            template_style = parsed_template_layouts[(STYLE_ITEM, template_layout.styleid)]

            if template_layout.threshold in existing_thresholds:
                new_threshold = self.__generate_new_threshold(existing_thresholds, template_layout.threshold)
                template_layout = template_layout._replace(threshold=new_threshold)
                existing_thresholds.add(new_threshold)
            parsed_content_layouts[(LAYOUT_ITEM, layout_id)] = template_layout
            parsed_content_layouts[(STYLE_ITEM, template_style.id)] = template_style



    def __match_any_layout(self, theme_layout, content_layouts):
        for layout in list(content_layouts.values()):
            if theme_layout.name == layout.name:
                return self.matching_layout(match=True, layout_id=layout.id)
        return self.matching_layout(match=False, layout_id="")

    def __generate_new_threshold(self, existing_thresholds, threshold):
        new_threshold = threshold
        while new_threshold in existing_thresholds:
            new_threshold += 1
        return new_threshold