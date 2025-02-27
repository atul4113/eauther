from django.shortcuts import get_object_or_404
from src.lorepo.filestorage.models import FileStorage
from src.xml_parsers.EchoXMLGenerator import OutputEchoXMLGenerator


class LessonCopyParser(OutputEchoXMLGenerator):
    def __init__(self, new_author, *args, **kwargs):
        super(LessonCopyParser, self).__init__(*args, **kwargs)

        self._new_author = new_author
        self._pages_to_extract = kwargs.get('pages_to_extract', None)
        self._page_index = 0
        self._is_folder = False
        self._is_removing_page = False
        self._parent_name = [None]

    def start_element(self, name, attrs):
        if name == 'page':
            if not self._parent_name[-1] and not self._is_folder:
                if self._pages_to_extract and self._page_index in self._pages_to_extract:
                    self._is_removing_page = True
                    self._page_index += 1
                    return

            href = attrs['href']
            pageFile = get_object_or_404(FileStorage, pk=href)

            attrs['href'] = str(pageFile.getCopy(self._new_author).id)
            self._page_index += 1

        if name == 'folder':
            self._is_folder = True

        self._parent_name.append(attrs.get('name', None))

        super(LessonCopyParser, self).start_element(name, attrs)

    def end_element(self, name):
        self._parent_name.pop()

        if name == 'folder':
            self._is_folder = False

        if name == 'page':
            if self._is_removing_page:
                self._is_removing_page = False
                return

        super(LessonCopyParser, self).end_element(name)
