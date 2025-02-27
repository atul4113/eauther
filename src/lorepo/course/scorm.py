import settings
from django.template import loader
from django.template.context import Context
from xml.dom.minidom import parseString
from src.lorepo.exchange.models import ExportVersions

def store_scorm_manifest(my_zip, course, version):
    manifest = create_manifest(course, version)
    my_zip.writestr('imsmanifest.xml', manifest)

def create_manifest(course, version):
    context = Context({'course' : course,
                       'settings': settings})
    if int(version) == ExportVersions.SCORM_2004.type:
        template = 'initdata/course/imsmanifest_2004.xml'
    else:
        template = 'initdata/course/imsmanifest_1_2.xml'
    manifest = loader.get_template(template).render(context)
    doc = parseString(manifest)
    organization = doc.getElementsByTagName('organization')[0]
    course_title = doc.createElement('title')
    title = doc.createTextNode(course.name)
    course_title.appendChild(title)
    organization.appendChild(course_title)
    resources = doc.getElementsByTagName('resources')[0]
    add_ebooks(doc, organization, resources, course.get_eBooks())
    add_chapters(doc, organization, resources, course.get_structure())
    return doc.toxml(encoding='utf-8')

def add_chapters(doc, parent, resources, chapters):
    for chapter in chapters:
        item = doc.createElement('item')
        item.setAttribute('identifier', 'chapter-%s' % chapter['node_id'])
        title = doc.createElement('title')
        title_text = doc.createTextNode(chapter['name'])
        title.appendChild(title_text)
        item.appendChild(title)
        add_chapters(doc, item, resources, chapter['kids'])
        for lesson_item in chapter['lessons']:
            add_lesson(doc, lesson_item, item, resources)
        parent.appendChild(item)

def add_ebooks(doc, parent, resources, ebooks):
    for ebook in ebooks:
        add_lesson(doc, ebook, parent, resources)

def add_lesson(doc, lesson_item, item, resources):
    lesson = doc.createElement('item')
    lesson.setAttribute('identifier', 'lesson-%s' % lesson_item['id'])
    lesson.setAttribute('identifierref', 'resource-%s' % lesson_item['id'])
    lesson_title = doc.createTextNode(lesson_item['name'])
    title = doc.createElement('title')
    title.appendChild(lesson_title)
    lesson.appendChild(title)
    item.appendChild(lesson)
    resource = doc.createElement('resource')
    resource.setAttribute('identifier', 'resource-%s' % lesson_item['id'])
    resource.setAttribute('type', 'webcontent')
    resource.setAttribute('adlcp:scormType', 'asset')
    resource.setAttribute('href', '%s/index.html' % lesson_item['id'])
    file_el = doc.createElement('file')
    file_el.setAttribute('href', '%s/index.html' % lesson_item['id'])
    resource.appendChild(file_el)
    resources.appendChild(resource)