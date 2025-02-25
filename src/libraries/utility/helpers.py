import uuid

from django.shortcuts import _get_queryset
import re
from django.core.files.storage import default_storage
from django.urls import reverse
from django.utils.timezone import now
from libraries.utility.decorators import cached


def get_object_or_none(klass, *args, **kwargs):
    queryset = _get_queryset(klass)
    results = queryset.filter(*args, **kwargs)
    return results[0] if len(results) > 0 else None


def get_values_per_page(request, key, max_value, default_value=10):
    values_per_page_session = request.session.get('values_per_page_%s' % key, None)
    values_per_page_get = request.GET.get('values_per_page', None)

    if values_per_page_session and not values_per_page_get:
        if values_per_page_session == 'all':
            values_per_page = max_value
            values_per_page_string = 'all'
        else:
            values_per_page = int(values_per_page_session)
            values_per_page_string = str(values_per_page_session)

    elif values_per_page_session and values_per_page_get:
        if values_per_page_get == 'all':
            values_per_page = max_value
            values_per_page_string = 'all'
        else:
            values_per_page = int(values_per_page_get)
            values_per_page_string = str(values_per_page)

    elif not values_per_page_session and values_per_page_get:
        if values_per_page_get == 'all':
            values_per_page = max_value
            values_per_page_string = 'all'
        else:
            values_per_page = int(values_per_page_get)
            values_per_page_string = str(values_per_page)

    else:
        values_per_page = default_value
        values_per_page_string = str(default_value)

    if values_per_page_string != values_per_page_session:
        request.session['values_per_page_%s' % key] = values_per_page_string

    return values_per_page, values_per_page_string


def blobstore_upload_url(request, success_path, max_bytes_per_blob=None, max_bytes_total=None, rpc=None,
                         gs_bucket_name=None):
    """
    Replacement for the blobstore_upload_url function.
    This generates a URL for uploading files using Django's default file storage system.
    The URL is a simple path that can be used to upload a file directly to the server.

    :param request: Django request object
    :param success_path: The path to redirect to after a successful upload
    :param max_bytes_per_blob: (Optional) Maximum size per file blob
    :param max_bytes_total: (Optional) Maximum total size for all blobs
    :param rpc: (Optional) RPC object (not used in this version)
    :param gs_bucket_name: (Optional) Google Cloud bucket name (not used in this version)
    :return: URL for file upload
    """
    # Generate a URL for the success path after file upload
    upload_url = reverse(success_path)

    # Check if there is a proxy host in the request headers
    proxy_host = request.META.get('HTTP_PROXY_HOST')
    if not proxy_host:
        return upload_url

    # If a proxy host exists, modify the URL to use the proxy
    protocol, location = upload_url.split('://')
    host, full_path = location.split('/', 1)

    return f"{protocol}://{proxy_host}/{full_path}"


class Parameters(object): pass


def parse_query_dict(query_dict):
    """
    Translate a query dict of type 'a[123]':'some value' into class:
    params.a['123'] : 'some value'
    """
    parameters = Parameters()
    for name, item in query_dict.iterlists():
        match = re.search('(?P<name>\w+)(\[(?P<key>\w+)\])*', name)
        groupdict = match.groupdict()
        if not hasattr(parameters, groupdict['name']):
            parameters.__setattr__(groupdict['name'], {groupdict['key']: item})
        else:
            parameters.__getattribute__(groupdict['name'])[groupdict['key']] = item
    return parameters


def is_server_local(request):
    """
    Checks if the server is running in a local development environment.

    :param request: Django request object
    :return: True if the server is local, False otherwise
    """
    return request.META['SERVER_SOFTWARE'].startswith('Development')


class SingletonMixin(object):
    """
    Mixin that ensures only one instance of the model exists in the database. It caches the instance and deletes
    cached data when a new instance is saved.
    """

    @classmethod
    @cached(timeout=60 * 60 * 24 * 30, params_key=lambda cls: cls.__name__)
    def get(cls):
        """
        Returns the single instance of the model. If no instances exist, a new instance is created and saved.
        If multiple instances exist, all but one are deleted.

        :return: The single instance of the model
        """
        objects = list(cls.objects.all())
        if len(objects) == 0:
            o = cls()
            o.save()
            return o
        elif len(objects) == 1:
            return objects[0]
        else:
            for o in objects[1:]:
                o.delete()
            return objects[0]

    def save(self, *args, **kw):
        """
        Saves the instance and deletes the cached instance from the cache.

        :param args: Arguments passed to the save method
        :param kw: Keyword arguments passed to the save method
        :return: Result of the save operation
        """
        save_result = super(SingletonMixin, self).save(*args, **kw)
        self.__class__.get.delete_cached(self.__class__)
        return save_result


def generate_unique_gcs_path(prefix='uploads/', extension=None):
    """
    Generates a unique GCS path for file uploads based on a prefix and extension.

    :param prefix: The folder path or prefix to use (e.g., 'uploads/')
    :param extension: The file extension to append (optional)
    :return: A unique GCS path as a string
    """
    # Generate a unique identifier for the file
    unique_id = str(uuid.uuid4())

    # If an extension is provided, ensure it starts with a dot
    if extension and not extension.startswith('.'):
        extension = f".{extension}"

    # Format the date and time for a more structured path (optional)
    date_str = now().strftime('%Y/%m/%d')

    # Combine everything to form the GCS path
    gcs_path = f"{prefix}{date_str}/{unique_id}{extension if extension else ''}"

    return gcs_path



def filter_in_chunks(queryset, chunk_size=1000):
    """
    Filters a queryset in chunks, yielding each chunk for processing.

    :param queryset: The queryset to filter and process
    :param chunk_size: The number of records to fetch per chunk (default: 1000)
    :yield: A chunk of queryset records
    """
    # Get the total number of records in the queryset
    total_records = queryset.count()

    # Iterate through the queryset in chunks
    for start in range(0, total_records, chunk_size):
        # Fetch a chunk of records based on the chunk size
        chunk = queryset[start:start + chunk_size]

        # Yield the chunk for processing
        yield chunk
