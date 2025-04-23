import xml.dom.minidom as minidom
import datetime
import time
import logging
import random
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from PIL import Image
from io import BytesIO
from src.lorepo.filestorage.models import FileStorage

MAX_RETRIES = 10


def create_new_version(file_storage, new_owner, is_addon=False, comment='', shallow=False):
    """
    Creates a new version of the file storage.
    Main page and all pages are copied. New main page is updated
    with IDs of copied subpages. Version is incremented.
    """
    new_version = 0
    if file_storage.history_for is not None:
        history = FileStorage.objects.filter(history_for=file_storage.history_for, content_type=file_storage.content_type)
        for item in history:
            if item.version > new_version:
                new_version = item.version

    new_file = file_storage.getCopy(new_owner)
    new_file.version = new_version + 1
    new_file.meta = '{"comment":"%s"}' % comment  # JSON-style comment for this version
    if not (is_addon or shallow):
        id_mapping = create_new_subpages(new_file, comment)
        update_main_page(new_file, id_mapping)
    new_file.history_for = file_storage.history_for
    new_file.save()
    return new_file


def create_new_subpages(file_storage, comment=''):
    """
    Creates copies of all subpages.
    Returns a dict of old to new values mapping.
    """
    id_mapping = {}
    dom = minidom.parseString(file_storage.contents)
    pages = dom.getElementsByTagName('page')
    for page in pages:
        old_id = page.attributes['href'].value
        old_page = FileStorage.objects.get(pk=old_id)
        new_page = old_page.getCopy(file_storage.owner)
        new_page.meta = '{"comment":"%s"}' % comment  # JSON-style comment for this version
        id_mapping[old_id] = new_page.id
    return id_mapping


def update_main_page(file_storage, id_mapping):
    """
    Updates the main page of content with IDs of subpages copies.
    Each subpage is copied and gets a new ID which must be inserted
    into the main page for a valid reference.
    """
    dom = minidom.parseString(file_storage.contents)
    pages = dom.getElementsByTagName('page')
    if len(pages) != len(id_mapping):
        raise Exception('Invalid number of pages for the selected content')

    for page in pages:
        page.setAttribute('href', str(id_mapping[page.getAttribute('href')]))
    file_storage.contents = dom.toxml("utf-8")
    file_storage.save()


def resize_image(uploaded_file, width, height):
    """
    Resizes an image and saves it to the default storage.
    """
    with Image.open(uploaded_file.file) as img:
        img.thumbnail((width, height))
        output = BytesIO()
        img.save(output, format='PNG')
        output.seek(0)

        bucket = 'imported-resources'
        now = datetime.datetime.now()
        file_name = f'{bucket}/{uploaded_file.id}/{now.year}/{now.month}/{now.day}/{now.hour}/{now.minute}/thumbnail.png'
        default_storage.save(file_name, ContentFile(output.read()))

    return file_name


def create_xliff_filestorage(user, contents):
    """
    Creates a new FileStorage instance for XLIFF content.
    """
    now = datetime.datetime.now()
    fs = FileStorage(
        created_date=now,
        modified_date=now,
        content_type="application/x-xliff+xml",
        contents=contents,
        owner=user,
        version=1
    )
    fs.save()
    return fs


def get_reader(uploaded_file):
    """
    Returns a file-like object for reading the uploaded file.
    """
    retries_count = 0
    while retries_count < MAX_RETRIES:
        retries_count += 1
        try:
            return default_storage.open(uploaded_file.path)
        except Exception as e:
            logging.error(f'Retry {retries_count} for uploaded_file={uploaded_file.id}: {str(e)}')
            time.sleep(random.randint(0, 4))
    raise Exception(f'The maximum number of attempts for uploaded_file={uploaded_file.id} has been exceeded')


def store_file(file_name, mime_type, data):
    """
    Stores a file in the default storage.
    """
    with default_storage.open(file_name, 'w') as my_file:
        my_file.write(data)
    return file_name


def store_file_from_stream(file_name, mime_type, stream):
    """
    Stores a file in the default storage from a stream.
    """
    with default_storage.open(file_name, 'w') as my_file:
        stream.seek(0)
        data = stream.read(65536)
        while data:
            my_file.write(data)
            data = stream.read(65536)
    return file_name

def build_retry_params():
    """
    Returns a dictionary of retry parameters for file operations.
    These parameters can be used to configure retry logic in other functions.
    """
    return {
        'max_retries': 10,  # Maximum number of retries
        'initial_delay': 0.2,  # Initial delay between retries (in seconds)
        'backoff_factor': 2,  # Multiplier for increasing delay between retries
        'max_delay': 10,  # Maximum delay between retries (in seconds)
    }