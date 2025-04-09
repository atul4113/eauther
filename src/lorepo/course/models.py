from django.db import models
from src import settings
from src.lorepo.filestorage.models import FileStorage, UploadedFile
from src.lorepo.spaces.models import Space
from xml.dom import minidom
from src.lorepo.course.helpers import create_chapter_node, get_structure_chapters,\
    get_element_by_id, get_lessons_container, get_chapter_lessons,\
    get_or_create_node, get_or_create_child_node, get_child_nodes,\
    get_child_element_by
from src.lorepo.course.helpers import get_elements_by_id
import re
from django.template import loader
from django.template.context import Context
import logging
from src.lorepo.mycontent.models import Content
import src.libraries.utility.cacheproxy as cache


class Course(models.Model):
    name = models.CharField(max_length=200)
    structure_xml = models.ForeignKey(FileStorage, on_delete=models.DO_NOTHING)
    project = models.ForeignKey(Space, on_delete=models.DO_NOTHING)
    is_being_exported = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    modified_date = models.DateTimeField(auto_now=True, null=True)

    def __unicode__(self):
        return str(self.name)

    def save(self, *args, **kwargs):
        if self.pk is not None:
            cache.set("course_%s" % self.pk, self, 60)
        super(Course, self).save(*args, **kwargs)

    @staticmethod
    def get_cached_course(course_id):
        course = cache.get("course_%s" % course_id)
        if not course:
            course = Course.objects.get(pk=course_id)
            cache.set("course_%s" % course_id, course, 60)
        return course

    def save_structure_xml(self, parsed_xml):
        course, created = get_or_create_node(parsed_xml, 'course')
        course.setAttribute('name', self.name)
        self.structure_xml.contents = re.sub(r'[\n\t\r]', '', parsed_xml.toxml(encoding='utf-8'))
        self.structure_xml.save()
        cache.delete("course_%s" % self.id)

    def _set_content_url(self, parsed_xml, content_type, exported_lesson):
        content_elements = get_elements_by_id(parsed_xml, content_type, exported_lesson.content.pk)

        for content_element in content_elements:
            content_element.setAttribute('url', '%s/file/serve/%s' % (settings.BASE_URL, exported_lesson.zipped_content.pk))
            gs_string = exported_lesson.zipped_content.path
            content_element.setAttribute('gs', gs_string)

    def save_exported_lessons(self, exported_lessons):
        try:
            parsed_xml = minidom.parseString(self.structure_xml.contents)

            for exported_lesson in exported_lessons:
                self._set_content_url(parsed_xml, 'ebook', exported_lesson)
                self._set_content_url(parsed_xml, 'lesson', exported_lesson)

            # Sanity check - in past there were situations, when for unknown reason there was missing 'url' attribute
            # for some elements. In that case - raise and exception and stop exporting course (it should not be
            # imported to mCourser).

            lesson_elements = parsed_xml.getElementsByTagName('lesson')
            for lesson_element in lesson_elements:
                if not lesson_element.hasAttribute('url'):
                    logging.error('Error while checking exported lesson XML representation (missing url attribute')
                    logging.error(lesson_element)
                    raise SyntaxError()

            ebook_elements = parsed_xml.getElementsByTagName('ebook')
            for ebook_element in ebook_elements:
                if not ebook_element.hasAttribute('url'):
                    logging.error('Error while checking exported eBook XML representation (missing url attribute')
                    logging.error(ebook_element)
                    raise SyntaxError()

            self.save_structure_xml(parsed_xml)
        except SyntaxError as e:
            raise e
        except Exception as e:
            import traceback
            logging.error('Error while saving exported lessons updated XML structure.')
            logging.error(traceback.format_exc())
            raise e

    def save_structure(self, chapters, lessons, eBooks):
        context = Context({'name': self.name, 'id': self.pk})
        parsed_xml = minidom.parseString(loader.get_template('initdata/course/root.xml').render(context).encode('utf-8'))
        for chapter in chapters:
            chapter_lessons = get_chapter_lessons(chapter, lessons)
            create_chapter_node(parsed_xml, chapter, chapter_lessons)
        self.save_structure_xml(parsed_xml)
        self.add_eBooks(eBooks)

    def set_id(self):
        parsed_xml = minidom.parseString(self.structure_xml.contents)
        course_element = parsed_xml.getElementsByTagName('course')[0]
        if not course_element.hasAttribute('id') or course_element.getAttribute('id') == '':
            course_element.setAttribute('id', str(self.pk))
        self.save_structure_xml(parsed_xml)

    def get_structure(self):
        parsed_xml = minidom.parseString(self.structure_xml.contents)

        return get_structure_chapters(parsed_xml)

    def remove_chapter(self, chapter_id):
        parsed_xml = minidom.parseString(self.structure_xml.contents)
        element = get_element_by_id(parsed_xml, 'chapter', chapter_id)
        if element:
            lessons = element.getElementsByTagName('lesson')
            lessons_ids = []
            for l in lessons:
                lessons_ids.append(l.getAttribute('lesson-id'))
            if len(lessons_ids):
                self._remove_elements(lessons_ids, 'resource')
                parsed_xml = minidom.parseString(self.structure_xml.contents)
                element = get_element_by_id(parsed_xml, 'chapter', chapter_id)
            parent = element.parentNode
            parent.removeChild(element)
            self.save_structure_xml(parsed_xml)

    def add_lessons_to_chapter(self, lessons, chapter_id):
        parsed_xml = minidom.parseString(self.structure_xml.contents)
        parent = get_element_by_id(parsed_xml, 'chapter', chapter_id)
        if parent:
            lessons_container = get_lessons_container(parsed_xml, parent)
            for lesson in lessons:
                lesson_element = parsed_xml.createElement('lesson')
                lesson_element.setAttribute('lesson-id', lesson['id'])
                lesson_element.setAttribute('name', lesson['name'])
                lesson_element.setAttribute('version', lesson['version'])
                lessons_container.appendChild(lesson_element)
            parent.appendChild(lessons_container)
            self.save_structure_xml(parsed_xml)
        else:
            return False

    def add_eBooks(self, eBooks):
        parsed_xml = minidom.parseString(self.structure_xml.contents)
        parent, _ = get_or_create_node(parsed_xml, 'ebooks')
        parsed_xml.documentElement.appendChild(parent)
        for eBook in eBooks:
            eBook_element = get_element_by_id(parsed_xml, 'ebook', eBook['id'])
            if not eBook_element:
                eBook_element = parsed_xml.createElement('ebook')
                eBook_element.setAttribute('ebook-id', eBook['id'])
                eBook_element.setAttribute('name', eBook['name'])
                if 'version' in eBook:
                    eBook_element.setAttribute('version', eBook['version'])
                else:
                    content = Content.get_cached_or_none(id = eBook['id'])
                    if content:
                        eBook_element.setAttribute('version', str(content.file.version))
                    else:
                        eBook_element.setAttribute('version', '0')
                if 'resources' in eBook and len(eBook['resources']) > 0:
                    logging.info(eBook['resources'])
                    eBook_element.appendChild(eBook['resources'][0])
                parent.appendChild(eBook_element)
        self.save_structure_xml(parsed_xml)

    def get_eBooks(self):
        parsed_xml = minidom.parseString(self.structure_xml.contents)
        eBooks_elements = parsed_xml.getElementsByTagName('ebook')
        eBooks = []
        for eBook_element in eBooks_elements:
            ebook_id = eBook_element.getAttribute('ebook-id')
            eBook = {
                'name': eBook_element.getAttribute('name'),
                'id': ebook_id,
                'is_deleted': Content.get_cached(id=ebook_id).is_deleted
            }
            eBooks.append(eBook)
        return eBooks

    def get_lessons_ids(self):
        return self._get_elements_ids('lesson')

    def get_eBooks_ids(self):
        return self._get_elements_ids('ebook')

    def update_ebooks(self, ids):
        self._update_elements(ids, 'ebook')

    def update_lessons(self, ids):
        self._update_elements(ids, 'lesson')

    def _update_elements(self, ids, element_type):
        parsed_xml = minidom.parseString(self.structure_xml.contents)
        for element_id in ids:
            elements = get_elements_by_id(parsed_xml, element_type, element_id)
            for element in elements:
                content = Content.get_cached(id = element_id)
                element.setAttribute('name', content.title)
                element.setAttribute('version', str(content.file.version))
        self.save_structure_xml(parsed_xml)

    def get_lessons_versions(self, ids):
        return self._get_element_versions('lesson', ids)

    def get_ebook_versions(self, ids):
        return self._get_element_versions('ebook', ids)

    def _get_element_versions(self, element_type, ids):
        parsed_xml = minidom.parseString(self.structure_xml.contents)
        versions_dict = {}
        for element_id in ids:
            element = get_element_by_id(parsed_xml, element_type, element_id)
            if element and element.hasAttribute('version'):
                versions_dict[element_id] = element.getAttribute('version')
        return versions_dict

    def _get_elements_ids(self, element_type):
        parsed_xml = minidom.parseString(self.structure_xml.contents)
        lessons = parsed_xml.getElementsByTagName(element_type)
        return [int(lesson.getAttribute(element_type + '-id')) for lesson in lessons]

    def remove_lessons(self, lessons_ids):
        self._remove_elements(lessons_ids, 'lesson')
        self._remove_elements(lessons_ids, 'resource')

    def remove_eBooks(self, eBooks_ids):
        self._remove_elements(eBooks_ids, 'ebook')

    def _remove_elements(self, ids, element_type):
        parsed_xml = minidom.parseString(self.structure_xml.contents)
        for element_id in ids:
            while True:
                element = get_element_by_id(parsed_xml, element_type, element_id)
                if element:
                    parent = element.parentNode
                    parent.removeChild(element)
                    if not parent.hasChildNodes():
                        parent.parentNode.removeChild(parent)
                else:
                    break
        self.save_structure_xml(parsed_xml)

    def edit_resources(self, eBook_id, page_index, ids_to_add, ids_to_remove):
        parsed_xml = minidom.parseString(self.structure_xml.contents)
        eBook = get_element_by_id(parsed_xml, 'ebook', eBook_id)
        if eBook:
            _, resources_node = get_or_create_child_node(parsed_xml, eBook, 'resources')
            for resource_id in ids_to_add:
                current_resource_node = get_child_element_by(resources_node, {'resource-id': resource_id, 'page': page_index})
                if not current_resource_node:
                    resource_node = parsed_xml.createElement('resource')
                    resource_node.setAttribute('resource-id', resource_id)
                    resource_node.setAttribute('page', page_index)
                    resources_node.appendChild(resource_node)
            for resource_id in ids_to_remove:
                current_resource_node = get_child_element_by(resources_node, {'resource-id': resource_id, 'page': page_index})
                if current_resource_node and current_resource_node in resources_node.childNodes:
                    resources_node.removeChild(current_resource_node)
            eBook.appendChild(resources_node)
            self.save_structure_xml(parsed_xml)

    def get_resources(self, eBook_id, page_index):
        resources = []
        parsed_xml = minidom.parseString(self.structure_xml.contents)
        eBook = get_element_by_id(parsed_xml, 'ebook', eBook_id)
        resources_nodes = get_child_nodes(eBook, 'resource')
        for resource_node in resources_nodes:
            page = resource_node.getAttribute('page')
            resource_id = resource_node.getAttribute('resource-id')
            if page == page_index:
                resource = {
                    'id': resource_id,
                    'page': page,
                    'name': Content.get_cached(id=resource_id).title
                }
                resources.append(resource)
        return resources


class LessonAlreadyCreatedError(Exception):
    pass


class ExportedCourse(models.Model):
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING)
    uploaded_file = models.ForeignKey(UploadedFile, null=True, on_delete=models.DO_NOTHING)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    number_of_contents = models.IntegerField(default=0)

    def validate_lesson_created(self, content):
        if ExportedCourseLesson.objects.filter(exported_course=self, content=content).count() > 0:
            raise LessonAlreadyCreatedError("Duplicated call for creating lesson %s for course %s" % (content, self.course))


class ExportedCourseLesson(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    zipped_content = models.ForeignKey(UploadedFile, on_delete=models.DO_NOTHING)
    exported_course = models.ForeignKey(ExportedCourse, on_delete=models.DO_NOTHING)
    content = models.ForeignKey(Content, on_delete=models.DO_NOTHING)


##This model is not used anywhere
# class UpdateCourseLesson(models.Model):
#     course = models.ForeignKey(Course, on_delete=models.DO_NOTHING)
#     created_date = models.DateTimeField(auto_now_add=True)
#     lesson = models.ForeignKey(Content, on_delete=models.DO_NOTHING)


##This model is not used anywhere
# class UpdateCourseLessonsCount(models.Model):
#     course = models.ForeignKey(Course, on_delete=models.DO_NOTHING)
#     created_date = models.DateTimeField(auto_now_add=True)
    
#     count = models.IntegerField(default=0)
