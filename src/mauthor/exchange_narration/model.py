from xml.dom import minidom
from src.mauthor.localization.utils import get_parent
from src.libraries.utility.helpers import get_object_or_none
from src.lorepo.filestorage.models import FileStorage
import datetime
from src.lorepo.spaces.util import get_space_for_content
from src.lorepo.corporate.utils import get_publication_for_space
import io
import csv
from src import settings
from django.db import models
from src.lorepo.mycontent.models import Content
from django.template.loader import render_to_string
from bs4 import BeautifulSoup, Tag
import re

class ExportNarration(object):

    def __init__(self, content):
        self.doc = minidom.parseString(content.file.contents)
        self.content = content
        self.errors = []
        self.pages = []
        self.export_type = ''

    def set_export_type(self, export_type):
        self.export_type = export_type

    def get_pages(self, page_filter = None):
        page_elements = self.doc.getElementsByTagName('page')
        pages = []

        for index, page_element in enumerate(page_elements):
            name = page_element.getAttribute('name')
            href = page_element.getAttribute('href')
            page = Page( name = name, href = href, index = index + 1 )

            if page_filter:
                if page_filter(page_element):
                    pages.append( page )
            else:
                pages.append( page )

        return pages

    def set_pages(self):
        self.pages = self.get_pages()

    def get_narration_elements(self, page_doc):
        property_elements = page_doc.getElementsByTagName('property')
        narration_elements = [pe for pe in property_elements if pe.getAttribute('name') == 'Narration']
        return narration_elements

    def _get_narration_element_value(self, narration_element):
        is_valid = True if narration_element.hasChildNodes() and narration_element.firstChild.nodeType == narration_element.firstChild.TEXT_NODE else False
        value = narration_element.firstChild.nodeValue if is_valid else ''
        return value

    def _get_narration_element_module_name(self, narration_element):
        module_element = get_parent(narration_element, 1)
        module_name = module_element.getAttribute('id')
        return module_name

    def set_narrations(self):

        for page in self.pages:
            page_file = get_object_or_none(FileStorage, pk = page.href)

            if page_file:
                page_doc = minidom.parseString(page_file.contents)
                narration_elements = self.get_narration_elements(page_doc)

                for narration_element in narration_elements:
                    narration_value = self._get_narration_element_value(narration_element)
                    narration_module_name = self._get_narration_element_module_name(narration_element)
                    if self.export_type == 'html':
                        narration_value = narration_value.replace(r'\n', '<br />')
                    narration = Narration(value = narration_value, module_name = narration_module_name)
                    page.narrations.append(narration)

    def _get_project_name(self):
        assigned_space = get_space_for_content(self.content)
        if assigned_space.is_corporate():
            project = get_publication_for_space(assigned_space).parent
            return project.title
        else:
            return 'My Content'

    def _get_publication_name(self):
        assigned_space = get_space_for_content(self.content)
        if assigned_space.is_corporate():
            publication = get_publication_for_space(assigned_space)
            return publication.title
        else:
            return None

    def _get_lesson_name(self):
        interactive_content_elements = self.doc.getElementsByTagName('interactiveContent')
        lesson_name = interactive_content_elements[0].getAttribute('name') if len(interactive_content_elements) else None
        return lesson_name

    def _get_embed_url(self):
        return '%(host_name)s/embed/%(content_id)s' % {'host_name': settings.BASE_URL, 'content_id': self.content.id}

    def _create_header_row(self):
        # nazwa projektu, nazwa publikacji, nazwa lekcji, link embed, data eksportu
        project_name = self._get_project_name().encode('utf-8')
        publication_name = self._get_publication_name()
        if publication_name is not None:
            publication_name = publication_name.encode('utf-8')
        lesson_name = self._get_lesson_name()
        if lesson_name is not None:
            lesson_name = lesson_name.encode('utf-8')
        embed_url = self._get_embed_url().encode('utf-8')
        export_date = datetime.datetime.now()
        return [project_name, publication_name, lesson_name, embed_url, str(export_date).encode('utf-8')]

    def _create_first_rows(self):
        # nazwa strony, nazwa modulu, link embed z odwolaniem do strony
        rows = []

        for page in self.pages:
            page_name = page.name
            embed_url = self._get_embed_url() + '#%(page_index)s' % { 'page_index' : page.index }
            
            for narration in page.narrations:
                module_name = narration.module_name
                rows.append([page_name.encode('utf-8'), module_name.encode('utf-8'), embed_url])

        return rows

    def _create_second_rows(self):
        # narracja
        rows = []

        for page in self.pages:
            for narration in page.narrations:
                value = str(narration.value).encode('utf-8')
                rows.append([value])

        return rows

    def recreate_header_csv(self, export_file):
        header = self._create_header_row()
        data = io.StringIO()
        splitted = export_file.contents.split('\r\n')

        reader = csv.reader(splitted, delimiter = ',', quotechar = '|', quoting = csv.QUOTE_MINIMAL)
        writer = csv.writer(data, delimiter = ',', quotechar = '|', quoting = csv.QUOTE_MINIMAL)

        for i, row in enumerate(reader):
            if i == 0:
                writer.writerow(header)
            elif len(splitted) - 1 > i: # omit last line which is unnecessary empty line (by-product of slit line)
                writer.writerow(row)

        export_file.contents = data.getvalue()
        export_file.save()
        data.close()

    def create_csv(self, user):
        header_row = self._create_header_row()
        first_rows = self._create_first_rows()
        second_rows = self._create_second_rows()

        now = datetime.datetime.now()

        csv_file = FileStorage(owner = user, content_type = 'text/csv', created_date = now, modified_date = now)

        data = io.StringIO()
        writer = csv.writer(data, delimiter = ',', quotechar = '|', quoting = csv.QUOTE_MINIMAL)
        writer.writerow(header_row)
        writer.writerow('')

        for i in range(0, len(first_rows)):
            writer.writerow(first_rows[i])
            for row in second_rows[i][0].split(r'\n'):
                writer.writerow([row])

        csv_file.contents = data.getvalue()
        csv_file.save()
        data.close()

        return csv_file

    def get_context(self):
        context = {}

        context['project'] = self._get_project_name()
        context['publication'] = self._get_publication_name()
        context['lesson'] = self._get_lesson_name()
        context['url'] = self._get_embed_url()
        context['date'] = str(datetime.datetime.now())
        context['pages'] = self.pages

        return context

    def recreate_header_html(self, export_file):
        soup = BeautifulSoup(export_file.contents)
        context = self.get_context()

        def _create_new(className):
            previous_mapping = {
                'project' : 'Project:',
                'publication' : 'Publication',
                'lesson' : 'Lesson:',
                'date' : 'Date of export:'
            }
            wrapper = Tag(soup, 'span', { 'class' : className })
            wrapper.setString(' %s' % context[className])
            previous_element = soup.find('b', text = previous_mapping[className])
            previous_element.next.replaceWith(wrapper)

        project = soup.find('span', { 'class' : 'project' })
        if project:
            new_text = re.sub(str(project), ' %s' % context['project'], str(project))
            project.contents[0].replaceWith(new_text)
        else:
            _create_new('project')

        publication = soup.find('span', { 'class' : 'publication' })
        if publication:
            new_text = re.sub(str(publication), ' %s' % context['publication'], str(publication))
            publication.contents[0].replaceWith(new_text)
        else:
            _create_new('publication')

        lesson = soup.find('span', { 'class' : 'lesson' })
        if lesson:
            new_text = re.sub(str(lesson), ' %s' % context['lesson'], str(lesson))
            lesson.contents[0].replaceWith(new_text)
        else:
            _create_new('lesson')

        date = soup.find('span', { 'class' : 'date' })
        if date:
            new_text = re.sub(str(date), ' %s' % context['date'], str(date))
            date.contents[0].replaceWith(new_text)
        else:
            _create_new('date')

        export_file.contents = soup.renderContents()
        export_file.save()

    def create_html(self, user):
        context = self.get_context()

        rendered = render_to_string('exchange_narration/init.html', context)

        now = datetime.datetime.now()
        html_file = FileStorage(owner = user, content_type = 'text/html', created_date = now, modified_date = now)
        html_file.contents = str(rendered).encode('utf-8')
        html_file.save()

        return html_file

class Page(object):

    def __init__(self, name, href, index):
        self.name = name
        self.href = href
        self.index = index
        self.narrations = []
        
class Narration(object):

    def __init__(self, value, module_name):
        self.value = value
        self.module_name = module_name

class ExportedNarration(models.Model):

    content = models.ForeignKey(Content, on_delete=models.DO_NOTHING)
    export_file = models.ForeignKey(FileStorage, on_delete=models.DO_NOTHING)