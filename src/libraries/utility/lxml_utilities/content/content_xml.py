from collections import namedtuple
from functools import partial


class DEVICE_ORIENTATION(object):
    vertical = "vertical"
    horizontal = "horizontal"

LayoutTuple = namedtuple("layout", ["id", "name", "styleid", "is_default", "threshold", "use_device_orientation", "device_orientation", "was_replaced"])
LayoutTuple.vertical_device = partial(LayoutTuple, use_device_orientation=True, device_orientation=DEVICE_ORIENTATION.vertical, was_replaced=False)
LayoutTuple.horizontal_device = partial(LayoutTuple, use_device_orientation=True, device_orientation=DEVICE_ORIENTATION.horizontal, was_replaced=False)
LayoutTuple.no_device = partial(LayoutTuple, use_device_orientation=False, device_orientation=DEVICE_ORIENTATION.vertical, was_replaced=False)

StyleTuple = namedtuple("style", ["id", "name", "is_default", "css"])
AddonDescriptor = namedtuple('AddonDescriptor', ["addonId", "href"])

NEWEST_CONTENT_XML_VERSION = "2"
OLD_CONTENT_XML_VERSION = "1"

STYLE_ITEM = "style"
LAYOUT_ITEM = "layout"


class ParsedSemiResponsiveContent(object):

    def __init__(self, layouts, styles):
        self.layouts = layouts
        self.styles = styles

    def thresholds_set(self):
        return { layout.threshold for layout in list(self.layouts.values()) }

    def add_layouts(self, layouts):
        self.layouts.update(layouts)

    def add_styles(self, styles):
        self.styles.update(styles)

    def matching_threshold_layouts(self, threshold_sets):
        return {layout.id: layout for layout in list(self.layouts.values()) if layout.threshold in threshold_sets }

    def matching_threshold_styles(self, threshold_sets):
        result = {}
        for layout in (layout for layout in list(self.layouts.values()) if layout.threshold in threshold_sets):
            result[layout.styleid] = self.styles[layout.styleid]

        return result

    def layouts_ids_set(self):
        return { layout.id for layout in list(self.layouts.values()) }

    def styles_ids_set(self):
        return { style.id for style in list(self.styles.values()) }

    def __get_default_layout_style(self):
        return [(l, s) for l in list(self.layouts.values()) for s in list(self.styles.values()) if l.is_default and s.is_default][0]

    def __getitem__(self, item):
        if len(item) != 2:
            raise TypeError("Indices must be tuple of (STYLE_ITEM/LAYOUT_ITEM, string_id)")

        item_id = item[1]
        if STYLE_ITEM in item:
            return self.styles[item_id]
        elif LAYOUT_ITEM in item:
            return self.layouts[item_id]
        else:
            raise TypeError("Indices first argument must to be STYLE_ITEM or LAYOUT_ITEM")

    def __setitem__(self, key, value):
        if len(key) != 2:
            raise TypeError("Indices must be tuple of (STYLE_ITEM/LAYOUT_ITEM, string_id)")

        item_id = key[1]
        if STYLE_ITEM in key:
            self.styles[item_id] = value
        elif LAYOUT_ITEM in key:
            self.layouts[item_id] = value
        else:
            raise TypeError("Indices first argument must to be STYLE_ITEM or LAYOUT_ITEM")

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        import pprint
        layouts = pprint.pformat(self.layouts, indent=8, width=80)
        styles = pprint.pformat(self.styles, indent=8, width=80)
        return "{0} \n {1}".format(layouts, styles)

    default_layout_style = property(fget=__get_default_layout_style)


def content_parser_v2(content_root):
    layouts = [layout for layout in content_root.iterfind(".//layout")]
    layouts_map = {}
    validate_boolean = lambda x: x.capitalize() == "True"
    layouts_factory = {
        None: LayoutTuple.no_device,
        "horizontal": LayoutTuple.horizontal_device,
        "vertical": LayoutTuple.vertical_device
    }

    for layout in layouts:
        style_element = layout.find("style")
        threshold_element = layout.find("threshold")
        device_orientation = layout.xpath("./deviceOrientation/@value")
        device_orientation = device_orientation[0] if len(device_orientation) > 0 else None

        layout_id = layout.get("id")
        layouts_map[layout.get("id")] = layouts_factory[device_orientation](id=layout_id,
                                                    name=layout.get("name"),
                                                    styleid=style_element.get("id"),
                                                    is_default=validate_boolean(layout.get("isDefault", "False")),
                                                    threshold=int(threshold_element.get("width")))

    styles_map = {style.get("id"): StyleTuple(id=style.get("id"), name=style.get("name"),
                                              is_default=validate_boolean(style.get("isDefault", "False")),
                                              css=style.text)
                  for style in content_root.iterfind("./styles/style")}

    synced_styles, synced_layouts = sync_styles_and_layouts_before_version3(styles_map, layouts_map)
    return ParsedSemiResponsiveContent(synced_layouts, synced_styles)


def sync_styles_and_layouts_before_version3(styles, layouts):
    result_styles = {}
    result_layouts = {}
    for layout in list(layouts.values()):
        styleid = layout.styleid
        layout_id = layout.id

        if styleid in styles:
            new_style = StyleTuple(id=layout_id, name=layout.name, is_default=layout.is_default, css=styles[styleid].css)
        else:
            new_style = StyleTuple(id=layout_id, name=layout.name, is_default=layout.is_default, css="")

        result_layouts[layout_id] = layout._replace(styleid=new_style.id)
        result_styles[new_style.id] = new_style

    return result_styles, result_layouts


def content_parser_v1(content_root):
    style_element = content_root.find("style")
    css_value = style_element.text if style_element is not None else ""
    style_map = {
        "default": StyleTuple(id="default", name="default", is_default=True, css=css_value)
    }

    layouts_map = {
        "default": LayoutTuple.no_device(id="default", name="default", styleid="default", is_default=True, threshold=800)
    }

    return ParsedSemiResponsiveContent(layouts_map, style_map)


CONTENT_MAIN_XML_PARSERS = {
    "1": content_parser_v1,
    "2": content_parser_v2
}