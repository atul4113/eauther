from xml_parsers.EchoXMLGenerator import EchoXMLGenerator


class GetPagesListParser(EchoXMLGenerator):
    def __init__(self, *args, **kwargs):
        super(GetPagesListParser, self).__init__(*args, **kwargs)
        self.pages_list = []

    def get_pages_list(self):
        return self.pages_list

    def start_element(self, name, attr):
        if name == 'page':
            self.pages_list.append(attr['href'])

        super(GetPagesListParser, self).start_element(name, attr)