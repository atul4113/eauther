from collections import defaultdict

from deepdiff import DeepDiff


def etree_to_dict(t, ignore=None):
    """
    https://stackoverflow.com/questions/7684333/converting-xml-to-dictionary-using-elementtree
    :param t: lxml root element
    :return: xml parsed to json
    :param ignore: tuple where first element is tag name and second attribute value
    """


    d = {t.tag: {} if t.attrib else None}
    children = list(t)
    if children:
        dd = defaultdict(list)
        for dc in map(etree_to_dict, children, [ignore]*len(children)):
            for k, v in dc.items():
                dd[k].append(v)
        d = {t.tag: {k:v[0] if len(v) == 1 else v for k, v in dd.items()}}
    if t.attrib:
        d[t.tag].update(('@' + k, v) for k, v in t.attrib.items() if not ignore or not(t.tag == ignore[0] and k == ignore[1]))
    if t.text:
        text = t.text.strip()
        if children or t.attrib:
            if text:
              d[t.tag]['#text'] = text
        else:
            d[t.tag] = text
    return d


class ETreeXMLDiffMixin(object):

    def assert_are_equals(self, expected, input, ignore=None):
        """
        :param expected: lxml root element
        :param input: lxml root element
        :param ignore: tuple where first element is tag name and second attribute value
        """

        expected_dict = etree_to_dict(expected, ignore=ignore)
        input_dict = etree_to_dict(input, ignore=ignore)

        assert DeepDiff(expected_dict, input_dict, ignore_order=True) == {}

