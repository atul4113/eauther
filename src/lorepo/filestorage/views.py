import gc
import json
import logging

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render

import settings
from libraries.utility.BucketManager import FileStorageBucketManager
from libraries.utility.decorators import backend
from lorepo.filestorage.forms import UploadForm
from lorepo.filestorage.models import FileStorage, UploadedFile, SecureFile
from google.appengine.ext import blobstore
from google.appengine.api import images
import datetime
import cloudstorage
from lorepo.filestorage.utils import get_reader
from google.appengine.ext.blobstore import InternalError

from lorepo.util.requests import is_request_secure

SIZE_32_MB = 32 * 1024 * 1024 # should be google.appengine.ext.blobstore.MAX_BLOB_FETCH_SIZE
RETRY_COUNT = 5
GAE_LIMIT = 1024 * 1024 * 5
CACHE_MAXAGE = 60*60  # 3600*24*30 seems not working

def get_file(request, file_id):
    file = get_object_or_404(FileStorage, pk=file_id)
    if request.method == 'GET':
        response = HttpResponse(file.contents, content_type=file.content_type)
        response['Cache-Control'] = 'no-cache'
        return response
    else:
        if (not request.user.is_authenticated()) or (request.user!=file.owner):
            logging.error('Unauthorized request to save content')
            return HttpResponseForbidden('Permission Denied')

        file.contents = request.read()
        file.modified_date = datetime.datetime.now()
        file.save()
        response = HttpResponse("ok")
        return response

def blob_upload_dir(request):
    return HttpResponse(blobstore.create_upload_url('/file/upload'))

def upload(request):
    view_url = reverse('lorepo.filestorage.views.upload')
    if request.method == 'POST':
        try:
            form = UploadForm(request.POST, request.FILES)
            model = form.save(False)
            model.owner = request.user
            model.content_type = request.FILES['file'].content_type
            if model.content_type == 'application/mp4':
                model.content_type = 'video/mp4'
            model.filename = request.FILES['file'].name
            model.save()
            return HttpResponseRedirect(view_url + "?key=" + str(model.id))
        except:
            return HttpResponse("ERROR")

    key = request.GET.get('key', '???')
    if key == '???':
        return HttpResponse('/file/serve/???')
    model = UploadedFile.objects.get(pk=key)
    return render(request, 'editor/uploaded_file.json', {'file' : model})


def serve_blob(request, file_id):
    upload = get_object_or_404(UploadedFile, pk=file_id)
    return _serve_blob(request, upload)


def _serve_blob(request, upload):
    response = HttpResponse()
    response['Accept-Ranges'] = 'bytes'
    response['Content-Type'] = upload.content_type
    if upload.filename and upload.filename != '':
        response['content-disposition'] = 'filename="%s"' % upload.filename
    if upload.content_type != 'video/mp4' and upload.content_type != 'application/mp4':
        response['Cache-Control'] = "public, max-age=" + str(CACHE_MAXAGE)
        response['Pragma'] = 'Public'
    if upload.file.file.blobstore_info is not None:
        blob_key = str(upload.file.file.blobstore_info.key())
        size = upload.file.file.blobstore_info.size
    else:
        blob_key = str(upload.file)
        stat = cloudstorage.stat(upload.path)
        size = stat.st_size

    if size >= SIZE_32_MB:
        response['X-AppEngine-BlobKey'] = blob_key
        if 'HTTP_RANGE' in request.META:
            response['X-AppEngine-BlobRange'] = request.META['HTTP_RANGE']
        return response

    reader = get_reader(upload)
    response = serve_file(request, response, blob_key, size, reader)
    gc.collect()
    return response

def serve_file(request, response, blob_key, size, reader):
    retry = 0
    while retry < RETRY_COUNT:
        try:
            if 'HTTP_RANGE' not in request.META and size < SIZE_32_MB:
                response.write(reader.read())
            else:
                response.status_code = 206
                range_string = request.META['HTTP_RANGE']
                try:
                    bytes_string = range_string.split('=')[1]
                except:
                    bytes_string = range_string.split(':')[1]
                limits = bytes_string.split('-')
                start = int(limits[0])
                if limits[1] != '':
                    end = int(limits[1])
                else:
                    end = size - 1
                to_read = end - start + 1
                reader.seek(start)
                while to_read > GAE_LIMIT:
                    response.write(reader.read(GAE_LIMIT))
                    to_read = to_read - GAE_LIMIT
                if to_read > 0:
                    response.write(reader.read(to_read))
                response['Content-Range'] = 'bytes %s-%s/%s' % (start, end, size)
            retry = RETRY_COUNT
        except InternalError as e:
            retry = retry + 1
            if retry == RETRY_COUNT:
                reader.close()
                raise e
    reader.close()
    return response

def image_thumbnail(request, file_id, width=150, height=150):
    width = int(width)
    height = int(height)
    if width > 2000 or height > 2000:
        raise Http404

    upload = get_object_or_404(UploadedFile, pk=file_id)
    if 'image' in upload.content_type:
        try:
            if upload.file.file.blobstore_info is not None:
                image = images.Image(blob_key=upload.file.file.blobstore_info)
            elif upload.path is not None:
                image = images.Image(filename='/gs' + upload.path)
            else:
                raise Http404
            image.resize(width, height)
            response = HttpResponse(content=image.execute_transforms(output_encoding=images.PNG), content_type='image/png')
        except images.BadImageError:
            response = HttpResponseRedirect("/media/images/no_thumbnail.png")
        except images.NotImageError:
            response = HttpResponseRedirect("/media/images/no_thumbnail.png")
    else:
        response = HttpResponseRedirect("/media/images/no_thumbnail.png")
    response['Cache-Control'] = "public, max-age=" + str(3600*24*30)
    return response

@login_required
def serve_secure(request, file_id):
    if not is_request_secure(request):
        return HttpResponseRedirect('%s%s' % (settings.MAUTHOR_BASIC_URL, request.get_full_path()))

    upload = get_object_or_404(SecureFile, pk=file_id)

    if not upload.has_access(request.user):
        raise Http404()
    return _serve_blob(request, upload)


@backend
def remove_old_gcs_async(request):
    payload = json.loads(request.body)
    logging.info("[backend task][filestorage]Removing from gcs: {}".format(payload['path']))
    FileStorageBucketManager().delete(payload['path'])

    return HttpResponse("ok")