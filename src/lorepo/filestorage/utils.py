

from cloudstorage import stat
from lorepo.filestorage.models import FileStorage
from libraries.utility.helpers import generate_unique_gcs_path
from google.appengine.api import images
import datetime
from google.appengine.ext.blobstore import BlobReader
import cloudstorage as gcs
from google.appengine.runtime.apiproxy_errors import DeadlineExceededError
import logging

from settings import get_bucket_name
from xml_parsers.explicit_parsers.get_pages_list_parser import GetPagesListParser
from xml_parsers.explicit_parsers.update_main_page_parser import UpdateMainPageParser

MAX_RETRIES = 10


def create_new_version(file_storage, new_owner, is_addon=False, comment='', shallow = False):
    '''Creates new version of the file storage.
    Main page and all pages are copied. New main page is updated
    with ids of copied subpages. Version is incremented.

    WARNING
    If shallow is True, then new version have old pages (they dont copy it)
    '''
    new_version = 0
    if file_storage.history_for is not None:
        item = FileStorage.objects.filter(history_for=file_storage.history_for, content_type=file_storage.content_type).order_by('-version').first()
        if item is None:
            new_version = 0
        else:
            new_version = item.version

    new_file = file_storage.getCopy(new_owner)
    new_file.version = new_version + 1

    new_file.meta = '{"comment":"%s"}' % comment #json style comment for this version
    if not (is_addon or shallow):
        id_mapping = create_new_subpages(new_file, comment)
        update_main_page(new_file, id_mapping)
    new_file.history_for = file_storage.history_for
    new_file.save()
    return new_file


def create_new_subpages(file_storage, comment=''):
    '''Creates copies of all subpages.
    Returns a dict of old to new values mapping.
    '''
    id_mapping = {}

    content_handler = GetPagesListParser()

    with file_storage as file_storage_content:
        content_handler.parse(file_storage_content)

    for old_id in content_handler.get_pages_list():
        old_page = FileStorage.objects.get(pk=old_id)
        new_page = old_page.getCopy(file_storage.owner)
        new_page.meta = '{"comment":"%s"}' % comment #json style comment for this version
        id_mapping[old_id] = new_page.id
    return id_mapping


def update_main_page(file_storage, id_mapping):
    '''Updates the main page of content with ids of subpages copies.
    Each subpages is copied and gets a new id which must be inserted
    into the main page for a valid reference.
    '''

    update_main_page_handler = UpdateMainPageParser(id_mapping)

    with file_storage as contents:
        update_main_page_handler.parse(contents)

    if len(id_mapping) != update_main_page_handler.get_changes_count():
        raise Exception('Invalid number of pages for the selected content')

    file_storage.contents = update_main_page_handler.get_output_value()
    file_storage.save()


def resize_image(uploaded_file, width, height):
    image = images.Image(blob_key=uploaded_file.file.file.blobstore_info)
    image.resize(width, height)
    resized = image.execute_transforms(output_encoding=images.PNG)

    bucket = get_bucket_name('imported-resources')
    file_name = generate_unique_gcs_path(bucket, 'thumbnail.png', uploaded_file.id)
    store_file(file_name, 'image/png', resized)

    return file_name


def create_xliff_filestorage(user, contents):
    now = datetime.datetime.now()
    fs = FileStorage(
                       created_date=now,
                       modified_date=now,
                       content_type="application/x-xliff+xml",
                       contents=contents,
                       owner=user,
                       version=1)
    fs.save()
    return fs


def get_reader(uploaded_file):
    retries_count = 0
    while retries_count < MAX_RETRIES:
        retries_count += 1
        try:
            if uploaded_file.file.file.blobstore_info is not None:
                return BlobReader(str(uploaded_file.file.file.blobstore_info.key()))
            else:
                return gcs.open(uploaded_file.path, retry_params=build_retry_params())
        except DeadlineExceededError:
            logging.error('Retry %s for uploaded_file=%s' % (retries_count, uploaded_file.id))
    raise DeadlineExceededError('The maximum number of attempts for uploaded_file=%s has been exceeded' % uploaded_file.id)


def get_file_size(uploaded_file):
    try:
        if uploaded_file.file.file.blobstore_info is not None:
            return uploaded_file.file.file.blobstore_info.size
        else:
            return stat(uploaded_file.path).st_size
    except DeadlineExceededError:
        logging.error('Error when accessing size of uploaded_file=%s' % uploaded_file.id)
    raise DeadlineExceededError('Error when accessing size of uploaded_file=%s' % uploaded_file.id)


def build_retry_params():
    return gcs.RetryParams(urlfetch_timeout=60, max_retry_period=600, min_retries=3, max_retries=10, initial_delay=0.2, backoff_factor=2, max_delay=10)


def store_file(file_name, mime_type, data):
    my_file = gcs.open(file_name, 'w', mime_type, retry_params=build_retry_params())
    my_file.write(data)
    my_file.close()
    return file_name


def store_file_from_stream(file_name, mime_type, stream):
    my_file = gcs.open(file_name, 'w', mime_type, retry_params=build_retry_params())
    stream.seek(0)
    data = stream.read(65536)
    while data:
        my_file.write(data)
        data = stream.read(65536)
    my_file.close()
    stream.close()
    return file_name


def open_file(file_name, mime_type):
    return gcs.open(file_name, 'w', mime_type, retry_params=build_retry_params())


def store_file_from_gcs_stream(to_file="filename", from_gcs_stream=None, mime_type=None):
    my_file = gcs.open(to_file, 'w', mime_type, retry_params=build_retry_params())
    data = from_gcs_stream.read(65536)
    while data:
        my_file.write(data)
        data = from_gcs_stream.read(65536)
    my_file.close()
    from_gcs_stream.close()
    return to_file
