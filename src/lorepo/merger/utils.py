import uuid

from src.libraries.utility.lxml_utilities.content.content_xml import StyleTuple, LayoutTuple
from lxml import etree


def ensure_unique_layouts_and_css_ids(layouts, styles, layouts_existing_ids, styles_existing_ids):
    result_layouts = {}
    result_styles = {}
    ids_conversions = {}
    for layout in list(layouts.values()):
        style_id = layout.styleid
        style = styles[style_id]
        layout_new_id = layout.id
        if layout.id in layouts_existing_ids:
            layout_new_id = generate_unique_uuid4(layouts_existing_ids)
            ids_conversions[layout.id] = layout_new_id

        if style_id in styles_existing_ids:
            style_id = generate_unique_uuid4(styles_existing_ids)

        new_style = StyleTuple(id=style_id, name=style.name, is_default=None, css=style.css)
        new_layout = LayoutTuple(id=layout_new_id, name=layout.name, styleid=style_id, is_default=None,
                                 threshold=layout.threshold, use_device_orientation=layout.use_device_orientation, device_orientation=layout.device_orientation,
                                 was_replaced=layout.was_replaced)

        layouts_existing_ids.add(new_layout.id)
        styles_existing_ids.add(new_style.id)
        result_layouts[new_layout.id] = new_layout
        result_styles[new_style.id] = new_style

    return result_layouts, result_styles, ids_conversions


def generate_unique_uuid4(existing_ids):
    unique = str(uuid.uuid4())
    while unique in existing_ids:
        unique = str(uuid.uuid4())

    return unique


def create_replace_map(from_layouts, to_layouts):
    result = {}
    for from_layout in list(from_layouts.values()):
        for to_layout in list(to_layouts.values()):
            if to_layout.threshold == from_layout.threshold:
                result[from_layout.id] = to_layout.id
                break

    return result


def replace_in_page_ids(contents, replace_map):
    parser = etree.XMLParser(strip_cdata=False)
    root = etree.fromstring(contents, parser=parser)
    page_version = int(root.get("version", 2))
    if page_version < 3:
        return contents

    for layout in root.iter("layout"):
        layout_id = layout.get("id")
        if layout_id in replace_map:
            layout.set("id", replace_map[layout_id])

    return etree.tostring(root, encoding="utf-8")