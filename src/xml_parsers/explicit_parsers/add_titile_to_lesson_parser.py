from xml_parsers.EchoXMLGenerator import OutputEchoXMLGenerator


class AddTitleToXMLParser(OutputEchoXMLGenerator):
    def __init__(self, title, *args, **kwargs):
        super(AddTitleToXMLParser, self).__init__(*args, **kwargs)

        self._title = title
        self.count = 0

    def start_element(self, name, attrs):
        if name == 'interactiveContent':
            if self.count == 0:
                attrs['name'] = self._title
            self.count += 1

        super(AddTitleToXMLParser, self).start_element(name, attrs)
