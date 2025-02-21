from django.shortcuts import _get_queryset
import re
import uuid
import datetime

from google.appengine.api import blobstore
from libraries.utility.decorators import cached


def get_object_or_none(klass, *args, **kwargs):
    queryset = _get_queryset(klass)
    results = queryset.filter(*args, **kwargs)
    return results[0] if len(results) > 0 else None

def get_values_per_page(request, key, max_value, default_value = 10):
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


def blobstore_upload_url(request, success_path,
                      max_bytes_per_blob=None,
                      max_bytes_total=None,
                      rpc=None,
                      gs_bucket_name=None):

    upload_url = blobstore.create_upload_url(success_path, max_bytes_per_blob, max_bytes_total, rpc, gs_bucket_name)

    proxy_host = request.META.get('HTTP_PROXY_HOST')
    if not proxy_host:
        return upload_url

    protocol, location = upload_url.split('://')
    host, full_path = location.split('/', 1)

    return protocol + '://' + proxy_host + '/' + full_path


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
            parameters.__setattr__(groupdict['name'], {groupdict['key'] : item})
        else:
            parameters.__getattribute__(groupdict['name'])[groupdict['key']] = item
    return parameters


def is_server_local(request):
    return request.META['SERVER_SOFTWARE'].startswith('Development')


class SingletonMixin(object):

    @classmethod
    @cached(timeout=60*60*24*30, params_key=lambda cls: cls.__name__)
    def get(cls):
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
        save_result = super(SingletonMixin, self).save(*args, **kw)
        self.__class__.get.delete_cached(self.__class__)
        return save_result


def generate_unique_gcs_path(bucket='bucket-name', name='name', *args):
    now = datetime.datetime.now()
    uuid_name = uuid.uuid4().int
    path = '%s/' % bucket

    for v in args:
        path = '%s/%s' % (path, str(v))
    path = '%s/%s/%s/%s/%s/%s/%d/%s' % (path, now.year, now.month, now.day, now.hour, now.minute, uuid_name, name)
    return path


def chunks(sequence, n=30):
    for i in range(0, len(sequence), n):
        yield sequence[i:i + n]


def filter_in_chunks(klass, **kwargs):
    params = {}
    in_filter_key = None
    in_filter_values = None
    for key, value in list(kwargs.items()):
        if key[-4:] == '__in':
            if in_filter_key is not None:
                raise Exception('Only one __in filter is supported')
            in_filter_key = key
            in_filter_values = value
        else:
            params[key] = value
    result = []
    if in_filter_key is None:
        return klass.objects.filter(**params)
    for chunk in chunks(in_filter_values):
        params[in_filter_key] = chunk
        result.extend(klass.objects.filter(**params))
    return result
