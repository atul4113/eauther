from xml_parsers.EchoXMLGenerator import OutputEchoXMLGenerator


class UpdateMainPageParser(OutputEchoXMLGenerator):
    """
    Change page url to provided map
    """

    def __init__(self, map, *args, **kwargs):
        super(UpdateMainPageParser, self).__init__(*args, **kwargs)

        self.__map = map
        self.__changes_count = 0

    def start_element(self, name, attr):
        if name == 'page':
            attr['href'] = str(self.__map[attr['href']])
            self.__changes_count += 1

        super(UpdateMainPageParser, self).start_element(name, attr)

    def get_changes_count(self):
        return self.__changes_count

