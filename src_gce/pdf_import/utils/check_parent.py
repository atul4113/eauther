def is_in_g_markup(xml):
    if "{http://www.w3.org/2000/svg}g" not in xml.tag:
        if "{http://www.w3.org/2000/svg}svg" not in xml.tag:
            return False
        else:
            return True
    return is_in_g_markup(xml.getparent())