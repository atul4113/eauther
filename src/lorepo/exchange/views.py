import io
import re
import json
import xml.dom.minidom
import os.path
import datetime
import logging
import copy

from django.utils.decorators import method_decorator
from django.views.generic.base import View, TemplateView
from google.appengine.api import urlfetch
from google.appengine.ext.deferred import deferred

import zipstream
from django.shortcuts import get_object_or_404

from libraries.utility.helpers import generate_unique_gcs_path
from lorepo.corporate.decorators import HasSpacePermissionMixin
from lorepo.filestorage.iterators import GcsIterator
from lorepo.filestorage.models import UploadedFile, FileStorage
from lorepo.mycontent.models import Content, ContentType, AddonToCategory
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED, BadZipfile
from google.appengine.ext import blobstore
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from lorepo.filestorage.forms import UploadForm
from django.http import HttpResponseRedirect, HttpResponse,\
    HttpResponseForbidden, Http404
from lorepo.spaces.util import get_private_space_for_user
from lorepo.exchange.models import ExportedContent, ExportVersions, ExportFails, ExportWOMIPages
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib import messages
from lorepo.spaces.models import Space
from libraries.utility.urlfetch import fetch
from libraries.utility.helpers import get_object_or_none
from django.template import loader
from django.template.context import Context
from libraries.utility.redirect import get_redirect
from lorepo.public.util import send_message
from libraries.utility.queues import trigger_backend_task
from django.core.mail import mail_admins
from lorepo.mycontent.service import add_content_to_space
from lorepo.exchange.utils import render_manifest, make_secret, RETRY_ERRORS
from lorepo.permission.decorators import has_space_access
from lorepo.mycontent.models import ContentType
from lorepo.permission.models import Permission
from google.appengine.ext.blobstore import InternalError
from lorepo.filestorage.utils import get_reader, store_file_from_stream, \
    open_file, store_file_from_gcs_stream, get_file_size
from libraries.utility.environment import get_app_version, get_versioned_module
from mauthor.metadata.util import get_metadata_values, get_page_metadata
from lorepo.permission.util import get_company_for_user
from mauthor.metadata.models import MetadataValue, PageMetadata
from libraries.utility.decorators import backend
from mauthor.localization.IcplayerZipped import IcplayerZipped
from mauthor.utility.decorators import LoginRequiredMixin
from settings import get_bucket_name, MAUTHOR_BASIC_URL

RETRY_COUNT = 20
XAPI_LIBS_DESCRIPTOR_PATH = 'lorepo/templates/exchange/tincan/descriptor.json'
PLAYER_ZIP_FILE_PATH = 'lorepo/templates/exchange/icplayer.zip'
WOMI_ZIP_FILE_PATH = 'lorepo/templates/exchange/womi.zip'
WOMI_HIDE_NAV_ZIP_FILE_PATH = 'lorepo/templates/exchange/womi-hide-nav.zip'

def _zip_uploaded_file(my_zip, stored_files, resource_types, file_id, path):
    upfiles = UploadedFile.objects.filter(pk=file_id)
    if upfiles.count() != 1:
        return {}
    else:
        upfile = upfiles[0]
    if upfile.filename:
        extension = os.path.splitext(upfile.filename)[1]
    else:
        extension = os.path.splitext(upfile.file.name.split('/')[-1])[1]
    filename = "%(path)sresources/%(name)s%(extension)s" % {'name':file_id, 'extension':extension, 'path':path}
    if not filename in stored_files:
        resource_types[filename] = upfile.content_type
        stored_files.add(filename)
        retry = 0
        while retry < RETRY_COUNT:
            try:
                reader = GcsIterator(get_reader(upfile))
                my_zip.write_iter(filename.encode('utf-8'), reader, compress_type=ZIP_DEFLATED,
                                  size=get_file_size(upfile))
                retry = RETRY_COUNT
            except InternalError as e:
                retry = retry + 1
                if retry == RETRY_COUNT:
                    logging.error('Problem with UploadedFile_id: %s' % upfile.id)
                    import traceback
                    logging.error(traceback.format_exc())
                    raise e
    return {file_id: "%(name)s%(extension)s" % {'name':file_id, 'extension':extension}}

def _update_resource_urls_to_locals(contents, local_urls):
    pattern_string = '(http:\/\/www\.(mauthor|minstructor)\.com)?\/file\/serve\/%(id)s'
    for file_id, filename in list(local_urls.items()):
        pattern = pattern_string % { 'id' : file_id }
        new = '../resources/%(filename)s' % {'filename' : filename}
        new = new.encode('utf-8')
        pattern = pattern.encode('utf-8')

        contents = re.sub(pattern, new, contents)
    return contents

def fix_absolute_resources(contents):
    rules = [
        'https://www.%s/file/serve/' % settings.APP_NAME,
        'https://%s/file/serve/' % settings.APP_NAME,
        'http://www.%s/file/serve/' % settings.APP_NAME,
        'http://%s/file/serve/' % settings.APP_NAME,
        '//www.%s/file/serve/' % settings.APP_NAME,
        '//%s/file/serve/' % settings.APP_NAME
    ]
    for rule in rules:
        contents = contents.replace(rule, '/file/serve/')
    return contents

def _zip_xml_and_resources(name, my_zip, contents, stored_files, path):
    filename = "%(path)spages/%(name)s.xml" % {'name' : name, 'path' : path}
    contents = fix_absolute_resources(contents)
    urls = re.findall("[\(\"\';]/file/serve/\d+", contents)
    resource_types = {}
    local_urls = {}
    for url in urls:
        parts = url.split('/')
        lu = _zip_uploaded_file(my_zip, stored_files, resource_types, parts[3], path)
        local_urls.update(lu)
    contents = _update_resource_urls_to_locals(contents, local_urls)
    my_zip.writestr(filename.encode('utf-8'), contents, compress_type=ZIP_DEFLATED)
    return resource_types

def _zip_metadata(my_zip, content, resources, addon_urls, path):
    metadata = xml.dom.minidom.parseString("<metadata></metadata>")
    element = metadata.getElementsByTagName('metadata')[0]
    element.setAttribute("id", str(content.id))
    element.setAttribute("title", content.title)
    element.setAttribute("tags", content.tags)
    element.setAttribute("description", content.description)
    element.setAttribute("short_description", content.short_description)
    element.setAttribute("content_type", str(content.content_type))
    element.setAttribute("enable_page_metadata", str(content.enable_page_metadata))
    if content.icon_href:
        element.setAttribute("icon_href", content.icon_href)

    metadata_values = get_metadata_values(content)
    for value in metadata_values:
        entered_value = value.as_xml_node(metadata)
        element.appendChild(entered_value)

    page_metadata = get_page_metadata(content)
    content_doc = xml.dom.minidom.parseString(content.file.contents)
    pages_elements = content_doc.getElementsByTagName('page')
    index_dict = {}
    for index, page in enumerate(pages_elements):
        index_dict[page.getAttribute('id')] = str(index + 1)

    #filter out metadata for non-existing pages
    new_page_metadata = []
    if len(page_metadata) > 0:
        for pm in page_metadata:
            if pm.page_id in index_dict:
                new_page_metadata.append(pm)

    page_metadata = new_page_metadata

    #add metadata to xml file
    if len(page_metadata) > 0:
        pages = metadata.createElement('pages')
        for pm in page_metadata:
            page = metadata.createElement('page')
            page.setAttribute('page_id', pm.page_id)
            page.setAttribute('title', pm.title)
            page.setAttribute('tags', pm.tags)
            page.setAttribute('description', pm.description)
            page.setAttribute('short_description', pm.short_description)
            page.setAttribute('is_enabled', str(pm.is_enabled))
            page.setAttribute('page_index', index_dict[pm.page_id])
            for extended in pm.metadata_values:
                entered_value = extended.as_xml_node(metadata)
                page.appendChild(entered_value)
            pages.appendChild(page)
        element.appendChild(pages)

    resources_element = metadata.createElement('resources')
    for filename, content_type in list(resources.items()):
        resource_element = metadata.createElement('resource')
        resource_element.setAttribute('filename', filename)
        if content_type is not None:
            resource_element.setAttribute('content_type', content_type)
        else:
            resource_element.setAttribute('content_type', 'application/octet-stream')
        resources_element.appendChild(resource_element)
    element.appendChild(resources_element)

    addons_element = metadata.createElement('addons')
    for id, href in list(addon_urls.items()):
        addon_element = metadata.createElement('addon')
        addon_element.setAttribute('addonId', id)
        addon_element.setAttribute('href', href)
        addons_element.appendChild(addon_element)
    element.appendChild(addons_element)

    filename = "%smetadata.xml" % path
    my_zip.writestr(filename.encode('utf-8'), metadata.toxml("UTF-8"), compress_type=ZIP_DEFLATED)

def _zip_icon(my_zip, content, stored_files, resource_types, path):
    icon_type = {}
    match = re.match('/file/serve/(?P<id>\d+)', content.icon_href)
    if match:
        return _zip_uploaded_file(my_zip, stored_files, resource_types, match.group('id'), path)
    return icon_type

def _zip_addons(my_zip, f, path):
    addon_urls = {}
    doc = xml.dom.minidom.parseString(f.contents)
    with IcplayerZipped() as icplayerZipp:
        for node in doc.getElementsByTagName('addon-descriptor'):
            addon_id = node.getAttribute('addonId')
            href = node.getAttribute('href')

            if icplayerZipp.is_player_addon(addon_id):
                continue

            if -1 == href.find("www.lorepo.com") and -1 == href.find("//localhost"):  # need to ignore legacy www.lorepo.com url's and localhost
                addon_xml = get_object_or_none(Content, content_type=ContentType.ADDON, name=addon_id)

                if addon_xml is not None:
                    filename = "%saddons/%s.xml" % (path, addon_id)
                    my_zip.writestr(filename.encode("utf-8"), addon_xml.file.contents)
                    addon_urls[addon_id] = href
                    localpath = '../addons/%s.xml' % addon_id
                    f.contents = f.contents.replace(href.encode("utf-8"), localpath.encode("utf-8"))
    return addon_urls


def _zip_file_export(my_zip, content, path, template_path):
    template = loader.get_template(template_path)
    context = Context({'content': content, 'app_name': settings.APP_NAME})
    content = template.render(context)
    filename = '%(path)s' % {'path': path}
    my_zip.writestr(filename.encode("utf-8"), content.encode('utf-8'), ZIP_DEFLATED)


def _zip_offline_page(my_zip, content, path, template_path, xapi=False):
    if xapi is True:
        _zip_xapi_file_export(my_zip, content, 'index.html', template_path)
    else:
        _zip_file_export(my_zip, content, 'index.html', template_path)

    _zip_file_export(my_zip, content, path='%sjavascript/semi-responsive-layout-chooser.js' % path, template_path='exchange/semi-responsive-layout-chooser.js')
    _zip_file_export(my_zip, content, path='%sjavascript/screen.js' % path, template_path='exchange/screen.js')


def _zip_scorm_manifest(my_zip, content, path, version):
    rendered = render_manifest(content, version)
    filename = '%simsmanifest.xml' % path
    my_zip.writestr(filename.encode("utf-8"), rendered.encode('utf-8'), ZIP_DEFLATED)


def _zip_xapi(my_zip, content, path):
    with open(XAPI_LIBS_DESCRIPTOR_PATH) as f:
        desc = json.load(f)
    for entry in desc:
        with open(entry['src']) as src_file:
            body = src_file.read()
            filepath = "%s%s" % (path, entry['dest'])
            my_zip.writestr(filepath.encode("utf-8"), body.encode('utf-8'), ZIP_DEFLATED)


def _zip_xapi_file_export(my_zip, content, path, template_path):
    template = loader.get_template(template_path)
    context = Context({"lessonTitle": content.title,
                       "lessonIRI": content.id,
                       "lessonDescription": content.description,
                       'app_name' : settings.APP_NAME})
    body = template.render(context)
    filename = '%(path)s' % {'path': path}
    my_zip.writestr(filename.encode('utf-8'), body.encode('utf-8'), ZIP_DEFLATED)


def zip_content(content, my_zip, path="", version=ExportVersions.SCORM_2004.type):
    stored_files = set()
    content = copy.deepcopy(content)
    _fix_addons_urls(content.file)

    if int(version) in (ExportVersions.WOMI.type, ExportVersions.WOMI_HIDE_NAV.type):
        womi_zip_file_path = WOMI_ZIP_FILE_PATH if int(version) == ExportVersions.WOMI.type else WOMI_HIDE_NAV_ZIP_FILE_PATH
        womi_assets_zip = ZipFile(womi_zip_file_path, 'r')
        for name in womi_assets_zip.namelist():
            data = womi_assets_zip.read(name)
            my_zip.writestr(path + name.encode('utf-8'), data, compress_type=ZIP_DEFLATED)

    addon_urls = _zip_addons(my_zip, content.file, path)
    resource_types = {}
    doc = xml.dom.minidom.parseString(content.file.contents)
    for node in doc.getElementsByTagName('page'):
        href = node.getAttribute('href')
        href = re.findall('\d+', href)[0]
        page = FileStorage.objects.get(pk=href)
        types = _zip_xml_and_resources(href, my_zip, page.contents, stored_files, path)
        resource_types.update(types)
        node.setAttribute('href', (href + '.xml').encode("utf-8"))
    content.file.contents = doc.toxml("utf-8")
    rt = _zip_xml_and_resources('main', my_zip, content.file.contents, stored_files, path)
    resource_types.update(rt)
    if content.icon_href is None:
        data = fetch(settings.LESSON_DEFAULT_ICON)
        data = io.StringIO(data)
        bucket = get_bucket_name('default-icon')
        file_name = generate_unique_gcs_path(bucket, 'icon', content.id)
        store_file_from_stream(file_name, 'image/png', data)
        blob_key = blobstore.create_gs_key('/gs' + file_name)
        upfile = UploadedFile()
        upfile.path = file_name
        upfile.file = str(blob_key)
        upfile.filename = 'default_presentation.png'
        upfile.content_type = 'image/png'
        upfile.save()
        content.icon_href = '/file/serve/%s' % upfile.pk
    icon_type = _zip_icon(my_zip, content, stored_files, resource_types, path)
    content.icon_href = _update_resource_urls_to_locals(content.icon_href, icon_type)
    _zip_metadata(my_zip, content, resource_types, addon_urls, path)

    if int(version) == ExportVersions.SCORM_XAPI.type:
        _zip_xapi(my_zip, content, path)
        _zip_offline_page(my_zip, content, path, template_path='exchange/tincan/index.html', xapi=True)
    elif int(version) == ExportVersions.HTML_5.type:
        _zip_offline_page(my_zip, content, path, template_path='embed/offline_html5.html')
    elif int(version) == ExportVersions.SCORM_1_2.type or int(version) == ExportVersions.SCORM_2004.type:
        _zip_offline_page(my_zip, content, path, template_path='embed/offline.html')
        _zip_scorm_manifest(my_zip, content, path, version)
    else:
        logging.debug('Version number (' + str(version) + ') is not supported')


class FetchException(Exception):
    def __init__(self, value):
        self.parameter = value

    def __str__(self):
        return repr(self.parameter)


def _fix_addons_urls(f):
    doc = xml.dom.minidom.parseString(f.contents)
    for node in doc.getElementsByTagName('addon-descriptor'):
        href = node.getAttribute('href')
        if href.startswith('http://') or href.startswith('//') or href.startswith('https://'):
            node.setAttribute('href', '/proxy/get?url=' + href)
    f.contents = doc.toxml('utf-8')
    f.save()


def _zip_content(content, user_id, version=ExportVersions.SCORM_2004.type, path='', my_zip=None, include_player=True):
    my_file = None
    file_name = None
    if my_zip is None:
        bucket = get_bucket_name('export-packages')
        file_name = generate_unique_gcs_path(bucket, 'package.zip', content.id , user_id)
        my_file = open_file(file_name, 'application/zip')
        my_zip = zipstream.ZipFile(allowZip64=True)
    try:
        if int(include_player):
            player_zip = ZipFile(PLAYER_ZIP_FILE_PATH,'r')
            for name in player_zip.namelist():
                if name[-1] == '/':
                    continue
                data = player_zip.read(name)
                womi_path = 'js/' if int(version) in (ExportVersions.WOMI.type, ExportVersions.WOMI_HIDE_NAV.type) else ''
                my_zip.writestr(path + womi_path + name.encode('utf-8'), data, compress_type=ZIP_DEFLATED)
        zip_content(content, my_zip, path, version)
    finally:
        if my_file is not None:
            for data in my_zip:
                my_file.write(data)
            my_zip.close()
            my_file.close()
    return file_name


def exported_file(content, requester, scorm_version, include_player, file_title=None):
    from google.appengine.api.runtime import memory_usage
    logging.info("Current memory usage before export: %s", memory_usage().current())
    file_name = _zip_content(content, requester, version=scorm_version, include_player=include_player)
    upfile = UploadedFile()
    upfile.file = str(blobstore.create_gs_key('/gs' + file_name))
    upfile.path = file_name
    upfile.content_type = 'application/zip'
    upfile.title = file_title
    upfile.save()
    logging.info("Current memory usage after export: %s", memory_usage().current())
    return upfile


@backend
def export(request, content_id, user_id, version):
    content = None
    user = 'ID%s'%(user_id) #if code below throws before user is assigned we will mail user_id atleast
    try:
        content = Content.get_cached_or_404(id=content_id)
        user = get_object_or_404(User, pk=user_id)
        upfile = exported_file(content, user_id, version, True)
        exported_content = ExportedContent(content=content, export=upfile, version=version)
        exported_content.save()
        send_export_confirmation(exported_content, user)
    except RETRY_ERRORS as e:
        logging.exception('%s - retrying. If you see too much of these, you will need to investigate' % type(e).__name__)
        return HttpResponseForbidden()
    except Exception as e:
        import traceback
        logging.exception('Export failed')
        logging.exception(e)
        mail_admins('Export failed: content=%s, user=%s' % (content_id, user), traceback.format_exc())
        send_export_failure_notification(user, content)
    return HttpResponse("ok")


@backend
def export_async(request, content_id, session_id):
    file_title = '%s_%s' % (session_id, content_id)
    try:
        content = Content.get_cached_or_404(id=content_id)
        exported_file(content, 'mcourser', ExportVersions.SCORM_2004.type, False, file_title)
    except RETRY_ERRORS as e:
        logging.exception('%s - retrying. If you see too much of these, you will need to investigate' % type(e).__name__)
        return HttpResponseForbidden()
    except Exception as e:
        import traceback
        logging.exception('Export failed')
        logging.exception(e)
        mail_admins('mCourser Export failed: content=%s, session=%s' % (content_id, session_id), traceback.format_exc())
        ExportFails(content_id=content_id, session_id=session_id).save()
    return HttpResponse("ok")


@backend
def export_with_callback(request, content_id, user_id, version):
    content = None
    callback_url = None
    session_token = None
    include_player = True

    user = 'ID%s' % (user_id)  # if code below throws before user is assigned we will mail user_id atleast
    try:
        if request.body:
            payload = json.loads(request.body)
            callback_url = payload.get('callback_url', None)
            session_token = payload.get('session_token', None)
            include_player = payload.get('include_player', True)

        if callback_url is None or session_token is None:
            return HttpResponse("Export_with_callback callback or session_token is None, can not proceed")

        content = Content.get_cached_or_404(id=content_id)
        user = get_object_or_404(User, pk=user_id)
        upfile = exported_file(content=content, requester=user_id, scorm_version=version, include_player=include_player)
        exported_content = ExportedContent(content=content, export=upfile, version=version)
        exported_content.save()

        download_url = MAUTHOR_BASIC_URL + '/api/v2/file/serve/%s' % exported_content.export.id

        post_data = {
            'session_token': session_token,
            'status_code': 200,
            'status_message': 'OK',
            'lesson_id': content_id,
            'download_url': download_url,
        }

        from google.appengine.api.taskqueue import TaskRetryOptions
        options = TaskRetryOptions(task_retry_limit=3, min_backoff_seconds=10, max_doublings=1)
        deferred.defer(_send_callback_export_confirmation, callback_url, post_data, _retry_options=options)

    except RETRY_ERRORS as e:
        logging.exception(
            '%s - retrying. If you see too much of these, you will need to investigate' % type(e).__name__)
        return HttpResponseForbidden()
    except Exception as e:
        import traceback
        logging.exception('Export_with_callback failed')
        logging.exception(e)
        mail_admins('Export_with_callback failed: content=%s, user=%s' % (content_id, user), traceback.format_exc())
        send_export_failure_notification(user, content)
    return HttpResponse("ok")


def _send_callback_export_confirmation(callback_url, post_data):
    try:
        response = urlfetch.fetch(url=callback_url, payload=json.dumps(post_data),
                                  method=urlfetch.POST,
                                  headers={"Content-Type": "application/json"})
        if response.status_code != 200:
            import logging
            logging.error("export_with_callback POST received status code %d! post_data: %s" % (response.status_code, post_data))
            raise Http404 #we need it for retry reason
    except:
        import logging
        import traceback
        logging.error(
            "export_with_callback POST callback error post_data: %s" % (post_data))
        logging.error(traceback.format_exc())
        raise Http404  # we need it for retry reason

    return True


def trigger_export_async(request, content_id, session_id, secret):
    local_secret = make_secret(content_id, session_id)
    if local_secret != secret:
        return HttpResponseForbidden()
    file_title = '%s_%s' % (session_id, content_id)
    if UploadedFile.objects.filter(title = file_title).count():
        return HttpResponseForbidden()
    trigger_backend_task("/exchange/export_async/%s/%s" % (content_id, session_id), target=get_versioned_module('download'), queue_name='download')
    return HttpResponse("OK")

def is_lesson_created(request, content_id, session_id, secret):
    local_secret = make_secret(content_id, session_id)
    if local_secret != secret:
        return HttpResponseForbidden()
    fails = ExportFails.objects.filter(content_id=content_id, session_id=session_id)
    if fails.count():
        return HttpResponse('CreationError')
    file_title = '%s_%s' % (session_id, content_id)
    my_files = UploadedFile.objects.filter(title = file_title).order_by('-path')
    if my_files.count():
        upfile = my_files[0]
        response_dict = { 'path': upfile.path,
                 'lesson_id': upfile.id }
        return HttpResponse(json.dumps(response_dict))
    else:
        raise Http404

def send_export_failure_notification(user, content):
    subject = 'Presentation has not been successfully exported'
    context = Context({ 'content' : content, 'user' : user, 'app_name' : settings.APP_NAME })
    email = loader.get_template('exchange/export_failure.txt')
    rendered = email.render(context)
    send_message(settings.SERVER_EMAIL, [user.email], subject, rendered)

def _get_title_or_spacebar(content):
    return ' ' + content.title + ' ' if content else ' '

def send_export_confirmation(exported_content, user):
    subject = 'Presentation "%s" successfully exported' % exported_content.content.title
    context = Context({'exported_content': exported_content, 'user': user, 'settings': settings})
    email = loader.get_template('exchange/confirmation.txt')
    rendered = email.render(context)
    send_message(settings.SERVER_EMAIL, [user.email], subject, rendered)

@login_required
def create(request, content_id, version):
    is_version, _ = ExportVersions.check_and_get_type(version)

    if not is_version:
        messages.info(request, 'This export version is not supported. If you got that message by mistake, please contact us.')
    else:
        _trigger_creation(request, content_id, version)

    return HttpResponseRedirect('/exchange/list/%(content_id)s/' % {'content_id' : content_id})



@has_space_access(Permission.EXCHANGE_EXPORT)
def _trigger_creation(request, content_id, version):
    trigger_backend_task("/exchange/export/%(content_id)s/%(user_id)s/%(version)s" % {
                              'content_id' : content_id,
                              'user_id' : request.user.id,
                              'version' : version}, target=get_app_version()+'.download', queue_name='download')
    messages.info(request, 'Presentation export will now run in background. Once it is completed you will be notified by email')


@has_space_access(Permission.EXCHANGE_EXPORT)
def _trigger_creation_new(request, content_id, version):
    trigger_backend_task("/exchange/export/%(content_id)s/%(user_id)s/%(version)s" % {
        'content_id': content_id,
        'user_id': request.user.id,
        'version': version}, target=get_app_version() + '.download', queue_name='download')


@login_required
def list_exports(request, content_id, version=ExportVersions.SCORM_2004.type):
    content = Content.get_cached_or_404(id=content_id)
    exports = ExportedContent.objects.filter(content=content).order_by('-created_date')
    is_version, _ = ExportVersions.check_and_get_type(version)

    for export in exports:
        export.version_name = ExportVersions.get_nametag(export.version)

    if not is_version:
        messages.info(request,'This export version is not supported. If you got that message by mistake, please contact us.')
        return HttpResponseRedirect('/exchange/list/%(content_id)s' % {'content_id': content_id, 'version': version})

    _trigger_creation(request, content_id, version)
    if len(exports) == 0:
        return get_redirect(request)
    else:
        return render(request, 'exchange/list_exports.html', {'exports' : exports, 'content' : content})


@login_required
def show_exports_list(request, content_id, version=ExportVersions.SCORM_2004.type):
    content = Content.get_cached_or_404(id=content_id)
    exports = ExportedContent.objects.filter(content=content).order_by('-created_date')
    is_version, _ = ExportVersions.check_and_get_type(version)

    for export in exports:
        export.version_name = ExportVersions.get_nametag(export.version)
    return render(request, 'exchange/list_exports.html', {'exports' : exports, 'content' : content})

def _create_content(zipfile, user):
    metadata = xml.dom.minidom.parseString(zipfile.read("metadata.xml"))
    element = metadata.getElementsByTagName('metadata')[0]
    now = datetime.datetime.now()
    content = Content(
                      title = element.getAttribute('title'),
                      tags = element.getAttribute('tags'),
                      description = element.getAttribute('description'),
                      short_description = element.getAttribute('short_description'),
                      created_date = now,
                      modified_date = now,
                      author = user,
                      content_type = int(element.getAttribute('content_type')) if element.hasAttribute('content_type') else ContentType.LESSON,
                      )
    if element.hasAttribute('enable_page_metadata'):
        content.enable_page_metadata = element.getAttribute('enable_page_metadata')
    if element.getAttribute('icon_href'):
        content.icon_href = element.getAttribute('icon_href')
    return content

def _create_extended_metadata(content, zipfile, user):
    metadata = xml.dom.minidom.parseString(zipfile.read('metadata.xml'))
    root = metadata.getElementsByTagName('metadata')[0]
    company = get_company_for_user(user)
    for value in root.childNodes:
        if value.nodeName == 'metadata-value':
            metadata_value = MetadataValue(content=content, company=company)
            metadata_value.from_xml_node(value)
            metadata_value.page = None
            metadata_value.save()

def _create_page_metadata(content, zipfile, user):
    metadata = xml.dom.minidom.parseString(zipfile.read('metadata.xml'))
    pages = metadata.getElementsByTagName('page')
    company = get_company_for_user(user)
    for page in pages:
        page_metadata = PageMetadata()
        page_metadata.content = content
        page_metadata.page_id = page.getAttribute('page_id')
        page_metadata.title = page.getAttribute('title')
        page_metadata.tags = page.getAttribute('tags')
        page_metadata.description = page.getAttribute('description')
        page_metadata.short_description = page.getAttribute('short_description')
        page_metadata.is_enabled = page.getAttribute('is_enabled')
        page_metadata.save()
        for node in page.childNodes:
            if node.nodeName == 'metadata-value':
                extended_metadata = MetadataValue(content=content, company=company)
                extended_metadata.from_xml_node(node)
                extended_metadata.page = page_metadata
                extended_metadata.save()

def _update_resource_urls(data, resources):
    for old_id, new_id in list(resources.items()):
        data = data.replace('../resources/%(id)s' % {'id' : old_id}, '/file/serve/%(id)s' % {'id' : new_id})
    return data

def _store_main_file(zipfile, user, mappings, resources):
    now = datetime.datetime.now()
    data = zipfile.read('pages/main.xml')
    data = _update_resource_urls(data, resources)
    doc = xml.dom.minidom.parseString(data)
    for page in doc.getElementsByTagName('page'):
        page.setAttribute('href', str(mappings[page.getAttribute('href')]))

    metadata = xml.dom.minidom.parseString(zipfile.read("metadata.xml"))
    for metadata_addon in metadata.getElementsByTagName('addon'):
        for addon in doc.getElementsByTagName('addon-descriptor'):
            if metadata_addon.getAttribute('addonId') == addon.getAttribute('addonId'):
                addon.setAttribute('href', metadata_addon.getAttribute('href'))

    main_file = FileStorage(
                            created_date = now,
                            modified_date = now,
                            content_type = "text/xml",
                            contents = doc.toxml("utf-8"),
                            owner = user,
                            version = 1)
    main_file.save()
    return main_file

def _store_pages(zipfile, user, resources):
    mappings = {}
    now = datetime.datetime.now()
    for name in zipfile.namelist():
        match = re.match('pages/(?P<page_id>\d+.xml)', name)
        if match:
            data = zipfile.read(name)
            data = _update_resource_urls(data, resources)
            page = FileStorage(
                            created_date = now,
                            modified_date = now,
                            content_type = "text/xml",
                            contents = data,
                            owner = user)
            page.save()
            mappings[match.group('page_id')] = page.id
    return mappings


def _store_resources(zipfile, user):
    metadata = xml.dom.minidom.parseString(zipfile.read("metadata.xml"))
    types = {}
    for element in metadata.getElementsByTagName('resource'):
        types[element.getAttribute('filename')] = element.getAttribute('content_type')
    resources = {}
    for name in zipfile.namelist():
        match = re.match('resources/(?P<resource_id>\d+)(?P<extension>.+)', name)
        if match:
            mime_type = types['resources/' + match.group('resource_id') + match.group('extension')]
            bucket = get_bucket_name('imported-resources')
            file_name = generate_unique_gcs_path(bucket, name, user.id)
            with zipfile.open(name=name, mode="r") as resource_file:
                store_file_from_gcs_stream(to_file=file_name, mime_type=mime_type, from_gcs_stream=resource_file)
            blob_key = blobstore.create_gs_key('/gs' + file_name)
            upfile = UploadedFile()
            upfile.path = file_name
            upfile.file = str(blob_key)
            upfile.filename = match.group('resource_id') + match.group('extension')
            upfile.content_type = mime_type
            upfile.owner = user
            upfile.save()
            resources[match.group('resource_id') + match.group('extension')] = upfile.id
    return resources

@backend
def import_presentation_async(request, uploaded_id, user_id, space_id=None):
    content = None
    zipfile = None
    reader = None
    try:
        uploaded_file = get_object_or_404(UploadedFile, pk=uploaded_id)
        user = get_object_or_404(User, pk=user_id)
        reader = get_reader(uploaded_file)
        zipfile = ZipFile(reader)
        resources = _store_resources(zipfile, user)
        content = _create_content(zipfile, user)
        mappings = _store_pages(zipfile, user, resources)
        main_file = _store_main_file(zipfile, user, mappings, resources)
        content.file = main_file
        if content.icon_href:
            content.icon_href = _update_resource_urls(content.icon_href, resources)
        content.save()
        _create_extended_metadata(content, zipfile, user)
        _create_page_metadata(content, zipfile, user)
        main_file.history_for = content
        main_file.save()
        if not space_id:
            space = get_private_space_for_user(user)
        else:
            space = Space.objects.get(pk=space_id)
        add_content_to_space(content, space)
        #send_import_confirmation(content, user)
    except BadZipfile:
        send_bad_zipfile_notification(user)
    except Exception:
        import traceback
        logging.exception('Import failed')
        mail_admins('Import failed', traceback.format_exc())
        send_import_failure_notification(user, content)
    finally:
        if reader is not None:
            reader.close()
        if zipfile is not None:
            zipfile.close()
    return HttpResponse('ok')

def send_import_failure_notification(user, content = None):
    subject = 'Presentation %s has not been successfully imported' % (content or '')
    context = Context({ 'content' : content or '', 'user' : user, 'app_name' : settings.APP_NAME })
    email = loader.get_template('exchange/import_failure.txt')
    rendered = email.render(context)
    send_message(settings.SERVER_EMAIL, [user.email], subject, rendered)

def send_import_confirmation(content, user):
    subject = 'Presentation "%s" successfully imported' % (content.title)
    context = Context({'content': content, 'user': user, 'settings': settings})
    email = loader.get_template('exchange/import_confirmation.txt')
    rendered = email.render(context)
    send_message(settings.SERVER_EMAIL, [user.email], subject, rendered)

def send_bad_zipfile_notification(user):
    subject = 'Provided file is not a zipfile'
    context = Context({'user' : user, 'app_name' : settings.APP_NAME })
    email = loader.get_template('exchange/import_bad_zipfile.txt')
    rendered = email.render(context)
    send_message(settings.SERVER_EMAIL, [user.email], subject, rendered)

@login_required
@has_space_access(Permission.EXCHANGE_IMPORT)
def import_presentation(request, space_id=None):
    upload_url = blobstore.create_upload_url(request.path)
    next_url = request.REQUEST['next'] if 'next' in request.REQUEST else '/mycontent'
    if request.method == 'POST':
        if len(request.FILES) > 0:
            form = UploadForm(request.POST, request.FILES)
            uploaded_file = form.save(False)
            uploaded_file.save()
            url = "/exchange/import/%(file_id)s/%(user_id)s" % {'file_id' : uploaded_file.id, 'user_id' : request.user.id}
            if space_id:
                url = url + '/' + space_id
            trigger_backend_task(url, target=get_versioned_module('download'), queue_name='download')
            messages.info(request, 'Presentation import will now run in background. Once it is completed you will be notified by email')
            return HttpResponseRedirect(next_url)
        else:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/mycontent'))
    else:
        form = UploadForm()
    return render(request, 'exchange/upload.html', {'upload_url' : upload_url, 'form' : form, 'next' : next_url})


class ExportWOMIPagesView(LoginRequiredMixin, HasSpacePermissionMixin, TemplateView):
    permission = Permission.EXCHANGE_EXPORT
    template_name = 'exchange/womi-pages-export.html'

    def get_context_data(self, **kwargs):
        user = self.request.user
        content = get_object_or_404(Content, pk=self.kwargs.get('content_id'))
        exports = ExportWOMIPages.objects.filter(content=content, is_success=True)

        exports = sorted(exports, key=lambda o: o.created_date, reverse=True)

        return {
            'user': user,
            'content': content,
            'exports': exports
        }

    def get(self, request, start_export=False, *args, **kwargs):
        if start_export:
            context = self.get_context_data()
            hide_nav = self.request.GET.get('hide_nav')

            export_pages = ExportWOMIPages(
                content=context.get('content'),
                user=context.get('user'),
                hide_nav=bool(hide_nav)
            )

            export_pages.save()

            trigger_backend_task('/exchange/export/{}/womi/pages_async'.format(export_pages.id), queue_name='download')

            messages.info(request,
                          'Lesson pages export will now run in background. Once it is completed you will be notified by email.')

            return HttpResponseRedirect('/exchange/export/{}/womi/pages'.format(context.get('content').id))

        return super(ExportWOMIPagesView, self).get(request, start_export, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        hide_nav = self.request.GET.get('hide_nav')

        export_pages = ExportWOMIPages(
            content=context.get('content'),
            user=context.get('user'),
            hide_nav=bool(hide_nav)
        )

        export_pages.save()

        trigger_backend_task('/exchange/export/{}/womi/pages_async'.format(export_pages.id), queue_name='download')

        messages.info(request,
                      'Lesson pages export will now run in background. '
                      'Once it is completed you will be notified by email.')

        return HttpResponseRedirect('/exchange/export/{}/womi/pages'.format(context.get('content').id))
