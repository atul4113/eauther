import re
from xml.dom import minidom
from src.lorepo.mycontent.models import Content


def parse_serialized_toc(toc_string):
    toc_array = toc_string.split('&')
    pattern = r'(?P<name>.+)\[(?P<id>\d+)\]=(?P<parent>.+)'
    result = []

    for element in toc_array:
        m = re.match(pattern, element)
        if m:
            obj = {
                   'id': m.group('id'),
                   'parent': m.group('parent'),
                   'name': m.group('name')
                   }
            result.append(obj)
    return result


def get_or_create_node(parsed_doc, node_name):
    created = False
    node = parsed_doc.getElementsByTagName(node_name)[0] if len(parsed_doc.getElementsByTagName(node_name)) > 0 else None
    if not node:
        created = True
        node = parsed_doc.createElement(node_name)
    return node, created


def get_or_create_child_node(parsed_doc, parent, node_name):
    if parent.hasChildNodes():
        for child in parent.childNodes:
            if child.nodeName == node_name:
                return False, child
    return True, parsed_doc.createElement(node_name)


def create_chapter_node(parsed_doc, chapter, lessons):
    node_id = chapter['id']
    parent_id = chapter['parent']
    name = chapter['name']
    root, root_created = get_or_create_node(parsed_doc, 'chapters')
    if root_created:
        parsed_doc.documentElement.appendChild(root)

    node = get_element_by_id(parsed_doc, 'chapter', node_id)
    if not node:
        node = parsed_doc.createElement('chapter')
        node.setAttribute('name', name)
        node.setAttribute('chapter-id', node_id)

    lessons_container = get_lessons_container(parsed_doc, node)
    for lesson in lessons:
        lesson_node = parsed_doc.createElement('lesson')
        lesson_node.setAttribute('lesson-id', lesson['id'])
        lesson_node.setAttribute('name', lesson['name'])
        content = Content.get_cached_or_none(id = lesson['id'])
        if content:
            lesson_node.setAttribute('version', str(content.file.version))
        else:
            lesson_node.setAttribute('version', '0')
        lessons_container.appendChild(lesson_node)

    if lessons_container.hasChildNodes():
        node.appendChild(lessons_container)

    if parent_id == 'root':
        root.appendChild(node)
    else:
        parent = get_element_by_id(parsed_doc, 'chapter', parent_id)
        if not parent:
            parent = parsed_doc.createElement('chapter')
            parent.setAttribute('chapter-id', parent_id)
        parent.appendChild(node)


def get_child_element_by(parent, params):
    while parent.hasChildNodes():
        for child in parent.childNodes:
            found = True
            for key, value in list(params.items()):
                if not child.getAttribute(key) == value:
                    found = False
                    break
            if found:
                return child
        parent = parent.childNodes[0]
    return None


def get_element_by_id(parsed_doc, node_name, node_id):
    elements = parsed_doc.getElementsByTagName(node_name)
    for element in elements:
        if element.hasAttribute(node_name + '-id') and element.getAttribute(node_name + '-id') == str(node_id):
            return element
    return None


def get_elements_by_id(parsed_doc, node_name, node_id):
    elements_nodes = parsed_doc.getElementsByTagName(node_name)
    elements = []
    for element in elements_nodes:
        if element.hasAttribute(node_name + '-id') and element.getAttribute(node_name + '-id') == str(node_id):
            elements.append(element)
    return elements


def get_child_nodes(parent, node_name):
    nodes = []
    while parent.hasChildNodes():
        for child in parent.childNodes:
            if child.nodeName == node_name:
                nodes.append(child)
        parent = parent.childNodes[0]

    return nodes


def get_structure_chapters(parsed_doc):
    chapters = parsed_doc.getElementsByTagName('chapter')
    structure_chapters = []

    for chapter in chapters:
        node_id = chapter.getAttribute('chapter-id')
        name = chapter.getAttribute('name')
        lessons_container = get_lessons_container(parsed_doc, chapter)
        lessons = []
        for lesson in lessons_container.childNodes:
            lesson_id = lesson.getAttribute('lesson-id')
            content = Content.get_cached(id=lesson_id)
            lesson = { 'id' : lesson_id, 'name' : content.title, 'is_deleted': content.is_deleted }
            lessons.append(lesson)

        structure_chapter = {
            'node_id' : node_id,
            'name' : name,
            'kids' : [],
            'lessons' : lessons
        }
        if chapter.parentNode.nodeName == 'chapters':
            parent_id = 'root'
            structure_chapters.append(structure_chapter)
        else:
            parent_id = chapter.parentNode.getAttribute('chapter-id')
            parent = _find_parent(structure_chapters, parent_id)
            parent['kids'].append(structure_chapter)

    return structure_chapters


def _find_parent(chapters, parent_id):
    for chapter in chapters:
        if chapter['node_id'] == parent_id:
            return chapter
    return _find_parent(chapters[-1]['kids'], parent_id)


def get_lessons_container(parsed_doc, parent):
    lessons_container = None
    for node in parent.childNodes:
        if node.nodeName == 'lessons':
            return node
    if not lessons_container:
        return parsed_doc.createElement('lessons')


def get_chapter_lessons(chapter, lessons):
    results = []
    for lesson in lessons:
        if int(lesson['parent']) == int(chapter['id']):
            results.append(lesson)
    return results


def filter_course_lessons(lessons, course_lessons_ids):
    return [lesson for lesson in lessons if lesson.id not in course_lessons_ids]


def get_ebook_resources_node(parsed_xml, ebook_id):
    ebook_element = get_element_by_id(parsed_xml, 'ebook', ebook_id)
    if ebook_element:
        return get_child_nodes(ebook_element, 'resources')
    return []


def remove_unrelated_resources(course_xml):
    parsed_doc = minidom.parseString(course_xml)
    lessons = parsed_doc.getElementsByTagName('lesson')
    lesson_ids = []
    for l in lessons:
        lesson_ids.append(l.getAttribute('lesson-id'))
    resources = parsed_doc.getElementsByTagName('resource')
    for r in resources:
        resource_id = r.getAttribute('resource-id')
        if resource_id not in lesson_ids:
            r.parentNode.removeChild(r)
    return parsed_doc.toxml(encoding = 'utf-8')


def check_deleted_lessons(course):
    parsed_doc = minidom.parseString(course.structure_xml.contents)
    lessons = parsed_doc.getElementsByTagName('lesson')
    for l in lessons:
        lesson = Content.get_cached(id=l.getAttribute('lesson-id'))
        if lesson.is_deleted:
            return True
    ebooks = parsed_doc.getElementsByTagName('ebook')
    for l in ebooks:
        ebook = Content.get_cached(id=l.getAttribute('ebook-id'))
        if ebook.is_deleted:
            return True
    return False