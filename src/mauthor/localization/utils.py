from xml.dom import minidom
from django.template.loader import render_to_string
from src.lorepo.mycontent.models import Content
from src.lorepo.filestorage.models import FileStorage, UploadedFile
from django.conf import settings
from google.cloud import storage  # Use google-cloud-storage instead of App Engine's blobstore
from src.lorepo.filestorage.forms import UploadForm
import io
import logging
from src.lorepo.spaces.models import Space
import datetime
from src.mauthor.localization.exceptions import ContentException
from django.shortcuts import get_object_or_404
from src.lorepo.mycontent.service import add_content_to_space
from src.libraries.utility.helpers import generate_unique_gcs_path  # If needed for cloud storage, otherwise use defaults
from src.settings import get_bucket_name

# Initialize Google Cloud Storage client
storage_client = storage.Client()


def get_xml_base_for_content(content_id):
    contents = Content.objects.filter(pk=content_id)
    if len(contents) > 0:
        content = contents[0]
    else:
        raise ContentException('ID of presentation is invalid.')
    base_xml = minidom.parseString(content.file.contents)
    return base_xml


def get_xliff(xliff_path='initdata/xliff/base.xlf'):
    template = render_to_string(xliff_path)
    xliff_document = minidom.parseString(template)
    return xliff_document


def get_content(content_id):
    return Content.get_cached_or_404(id=content_id)


def get_text_node(target):
    return target.firstChild.data if target.hasChildNodes() else ''


def create_id_string(field, module):
    id_string = '%(module_id)s:%(module_name)s|%(property_name)s' % {'module_id': module.id, 'module_name': module.name,
                                                                     'property_name': field.name}
    if field.type is not None:
        id_string = id_string + '|' + field.type
    if field.list_name is not None:
        id_string = id_string + '|' + field.list_name
    if field.list_index is not None:
        id_string = id_string + '|' + str(field.list_index)
    return id_string


def resolve_id_string(id_string):
    elements = id_string.split('|')
    resolved_id_string = []
    resolved_id_string.extend(elements)
    if len(elements) == 2:
        resolved_id_string.extend([None, None, None])  # when only name and value are set
    elif len(elements) == 3:
        resolved_id_string.extend([None, None])  # when only name, value and type are set
    return resolved_id_string


def get_file(file_id):
    return FileStorage.objects.get(id=file_id)


def get_space(space_id):
    return get_object_or_404(Space, pk=space_id)


def create_upload_file(xliff, content_id):
    stream = io.StringIO()
    stream.write(xliff.print_document())

    bucket_name = get_bucket_name('export-packages')  # Assuming you have the bucket name
    bucket = storage_client.get_bucket(bucket_name)

    # Generate unique file name for the upload
    file_name = generate_unique_gcs_path(bucket_name, 'localization.xliff', content_id)

    # Upload the file to GCS
    blob = bucket.blob(file_name)
    blob.upload_from_string(stream.getvalue(), content_type='application/x-liff+xml')

    # Create an uploaded file record in the database
    uploaded_file = UploadedFile()
    uploaded_file.file = file_name  # Store GCS file path in the model
    uploaded_file.path = file_name
    uploaded_file.content_type = 'application/x-liff+xml'
    uploaded_file.save()

    return uploaded_file


def get_upload_url(url):
    # You can use GCS signed URLs if needed for uploading, but typically you handle this on the frontend
    # For now, using Django default file handling
    return default_storage.url(url)


def is_property_for_translation(property_element, addon_fields):
    return property_element.getAttribute('name') in addon_fields


def get_properties_for_translation(properties, addon_fields):
    return [property_element
            for property_element in properties
            if is_property_for_translation(property_element, addon_fields)]


def get_content_from_property(property_element):
    if property_element.getAttribute('type') == 'string':
        return property_element.getAttribute('value')
    if property_element.hasChildNodes():
        return property_element.firstChild.data
    return ''


def get_parent(property_element, level):
    parent = property_element.parentNode
    for i in range(0, level):
        parent = parent.parentNode
    return parent


def parent_is_list(property_element):
    return get_parent(property_element, 2).getAttribute('type') == 'list'


def calculate_counter(counter, last_properties_name, current_properties_name):
    if last_properties_name == (None, None):
        return 0, current_properties_name
    elif last_properties_name == current_properties_name:
        return counter + 1, current_properties_name
    else:
        return 0, current_properties_name


def is_empty(some_text):
    return some_text == ''


def get_upload_form(params=None):
    if params:
        return UploadForm(params[0], params[1])
    else:
        return UploadForm()


def get_uploaded_xliff(uploaded_file_id):
    uploaded_file = UploadedFile.objects.get(pk=uploaded_file_id)
    return minidom.parseString(uploaded_file.file.read())


def get_url_for_addon_descriptor(addon_descriptor):
    href = addon_descriptor.getAttribute('href')
    if href[-3:] == 'xml':
        return '%s%s%s' % (settings.BASE_URL, '/media', href.split('media')[1])


def handle_execution(execute, module):
    module_type = module.nodeName
    if module_type in execute:
        module = execute[module_type](module)
        module.name = module_type
    else:
        module = None
        msg = 'No module named %(module_type)s' % locals()
        logging.error(msg)
    return module


def filter_localization_properties(properties):
    return [property_element.getAttribute('name')
            for property_element in properties
            if property_element.getAttribute('isLocalized') == 'true' or property_element.getAttribute(
            'type') == 'narration']


def get_uploaded_file(request):
    form = get_upload_form((request.POST, request.FILES))
    model = form.save(False)
    model.owner = request.user
    model.content_type = request.FILES['file'].content_type
    model.filename = request.FILES['file'].name
    model.save()
    return model


def make_copy_and_put_into_space(space_id, content_id, user, xml):
    content = Content.objects.filter(pk=content_id)[0]
    now = datetime.datetime.now()
    file_storage = FileStorage(
        created_date=now,
        modified_date=now,
        content_type="text/xml",
        contents=xml.print_document(),
        owner=user
    )
    file_storage.version = 1
    file_storage.save()
    copy = Content(
        title='Localized for ' + content.title,
        created_date=now,
        modified_date=now,
        author=user,
        icon_href=content.icon_href,
        file=file_storage,
        tags=content.tags,
        description=content.description,
        content_type=content.content_type
    )
    copy.save()
    file_storage.history_for = copy
    file_storage.save()
    space = get_object_or_404(Space, pk=int(space_id))
    add_content_to_space(copy, space)
    return copy


def is_list_type(field):
    return field.list_name


def get_list_properties(properties, property_name):
    for property_element in properties:
        if property_element.getAttribute('name') == property_name:
            return property_element.getElementsByTagName('items')[0].getElementsByTagName('property')
    return []


def get_list_properties_by_name(list_properties, list_property_name):
    filtered_properties = []
    for list_property in list_properties:
        if list_property.getAttribute('name') == list_property_name:
            filtered_properties.append(list_property)
    return filtered_properties


def get_property_by_name(properties, property_name):
    for property_element in properties:
        if property_element.getAttribute('name') == property_name:
            return property_element
    return None


def make_page_copy(href, new_author):
    page_xml = get_file(href)
    created_date = datetime.datetime.now()
    copy_file = FileStorage(
        created_date=created_date,
        modified_date=created_date,
        content_type="text/xml",
        contents=page_xml.contents,
        owner=new_author)
    return copy_file


def set_or_create_text_node(document, element, data):
    if element.hasChildNodes():
        element.childNodes = []

    text_node = document.createTextNode(data)
    element.appendChild(text_node)


def generate_id():
    import string
    import random
    list_of_random_letters = random.sample(string.ascii_letters, 5)
    return ''.join(list_of_random_letters)
