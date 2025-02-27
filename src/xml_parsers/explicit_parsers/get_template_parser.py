from src.xml_parsers.EchoXMLGenerator import EchoXMLGenerator


class GetTemplateParser(EchoXMLGenerator):
    def __init__(self, *args, **kwargs):
        super(GetTemplateParser, self).__init__(out=None)

        self._entry_value = ''

    def start_element(self, name, attrs):
        if name == 'entry':
            key = attrs.get('key', '')

            if key == 'theme.href':
                self._entry_value = attrs.get('value', '')

        super(GetTemplateParser, self).start_element(name, attrs)

    def get_entry_attr(self):
        return self._entry_value
