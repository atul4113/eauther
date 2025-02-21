# -*- coding: utf-8 -*-
import json
import os
import re
import urllib.request, urllib.parse, urllib.error
import xml.dom.minidom
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, render
from libraries.utility.helpers import get_object_or_none, generate_unique_gcs_path
from lorepo.assets.models import AssetsOrPagesReplacementConfig
from lorepo.mycontent.models import Content
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden
from lorepo.filestorage.forms import UploadForm
from lorepo.assets.util import update_content_assets, update_asset_title,\
    delete_asset, _validate_assets_replacement_data, _replace_assets_in_lesson, _send_replacement_status_info, replace_content_page_names
from lorepo.permission.decorators import has_space_access
from lorepo.permission.models import Permission
from libraries.utility.queues import trigger_backend_task
from lorepo.filestorage.models import UploadedFile
from django.contrib.auth.models import User
from zipfile import ZipFile, BadZipfile
import mimetypes
import logging
from django.contrib import messages
from django.template.context import Context
from django.template import loader
from lorepo.public.util import send_message
from django.conf import settings
from django.core.mail import mail_admins
from lorepo.filestorage.utils import get_reader, store_file, create_new_version
from google.appengine.ext import blobstore
from libraries.utility.environment import get_versioned_module
from libraries.utility.decorators import backend
from lorepo.spaces.models import Space
from settings import get_bucket_name

MAX_ASSETS_RETRIES = 10

@login_required
@has_space_access(Permission.ASSET_BROWSE)
def browse_assets(request, content_id):
    content = Content.get_cached_or_404(id=content_id)
    upload_url = blobstore.create_upload_url('/assets/upload/%(content_id)s' % locals())
    upload_package_url = blobstore.create_upload_url('/assets/upload_package/%(content_id)s' % locals())
    form = UploadForm()
    content_type = request.POST.get('type', None)
    assets = content.getAssets()
    available_types = set([asset.content_type for asset in assets])
    currently_edited = (content.who_is_editing() is not None)
    if currently_edited:
       messages.warning(request, "In order to upload a new asset the lesson should not be opened in editor.")
    if content_type is not None and content_type != '':
        assets = [asset for asset in assets if asset.content_type == content_type]
    return render(request, 'assets/assets.html', {
                                        'content' : content,
                                        'assets' : assets,
                                        'upload_url' : upload_url,
                                        'upload_package_url' : upload_package_url,
                                        'form' : form,
                                        'content_type' : content_type,
                                        'available_types' : sorted(available_types),
                                        'currently_edited' : currently_edited
                                        })

@login_required
@has_space_access(Permission.ASSET_EDIT)
def rename_asset(request, content_id, href):
    # workaround dla serwera developerskiego
    if os.environ['SERVER_SOFTWARE'].find('Development') > -1:
        href = urllib.parse.unquote(href).decode('utf8')
    content = Content.get_cached_or_404(id=content_id)
    if request.method == 'POST':
        user_editing = content.who_is_editing()
        if user_editing is not None:
            messages.warning(request, 'Lesson is currently opened in editor by user <%s>, can\'t rename an asset.' % (user_editing))
            return HttpResponseRedirect('/assets/%(content_id)s' % locals())
        update_asset_title(content, href, request.POST.get('title', ''))
        return HttpResponseRedirect('/assets/%(content_id)s' % locals())
    else:
        assets = content.getAssets()
        asset = [asset for asset in assets if asset.href == href][0]
        return render(request, 'assets/rename.html', {'asset' : asset, 'content' : content})

@login_required
@has_space_access(Permission.ASSET_EDIT)
def upload_asset(request, content_id):
    content = Content.get_cached_or_404(id=content_id)
    if request.method == 'POST':
        if len(request.FILES) > 0:
            user_editing = content.who_is_editing()
            if user_editing is not None:
                messages.warning(request, 'Lesson is currently opened in editor by user <%s>, can\'t upload a new asset.' % (user_editing))
                return HttpResponseRedirect('/assets/%(content_id)s' % locals())
            form = UploadForm(request.POST, request.FILES)
            uploaded_file = form.save(False)
            uploaded_file.content_type = request.FILES['file'].content_type
            import cgi
            uploaded_file.filename = cgi.escape(request.FILES['file'].name, True).encode('ascii', 'ignore')
            uploaded_file.owner = request.user
            uploaded_file.title = request.POST.get('title', '')
            uploaded_file.save()
            update_content_assets(content, uploaded_file)
    return HttpResponseRedirect('/assets/%(content_id)s' % locals())

@login_required
@has_space_access(Permission.ASSET_REMOVE)
def delete_assets(request, content_id, href):
    content = Content.get_cached_or_404(id=content_id)
    user_editing = content.who_is_editing()
    if user_editing is not None:
        messages.warning(request, 'Lesson is currently opened in editor by user <%s>, can\'t upload a new asset.' % (user_editing))
        return HttpResponseRedirect('/assets/%(content_id)s' % locals())
    delete_asset(content, href)
    return HttpResponseRedirect('/assets/%(content_id)s' % locals())

@login_required
def upload_package(request, content_id):
    content = Content.get_cached_or_404(id=content_id)
    if request.method == 'POST':
        if len(request.FILES) > 0:
            form = UploadForm(request.POST, request.FILES)
            uploaded_file = form.save(False)
            uploaded_file.content_type = request.FILES['file'].content_type
            import cgi
            uploaded_file.filename = cgi.escape(request.FILES['file'].name, True).encode('ascii', 'ignore')
            uploaded_file.owner = request.user
            uploaded_file.save()
            trigger_backend_task('/assets/process_package_async/%s/%s/%s' % (content_id, uploaded_file.id, request.user.id),
                                 target=get_versioned_module('download'),
                                 queue_name='download')
            messages.info(request, 'Your assets package will be imported in background. You will be notified by email when it\'s finished')
    return HttpResponseRedirect('/assets/%(content_id)s' % locals())

@backend
def process_package_async(request, content_id, file_id, user_id):
    content = Content.get_cached_or_404(id=content_id)
    user = get_object_or_404(User, pk=user_id)
    reader = None
    zipfile = None

    try:
        if content.who_is_editing() is not None:
            retries = int(request.META['HTTP_X_APPENGINE_TASKRETRYCOUNT'])
            if retries > MAX_ASSETS_RETRIES:
                send_failure_confirmation(content, user, 'assets/failure.txt')
                return HttpResponse("OK")
            else:
                return HttpResponseForbidden()
        content.set_user_is_editing(user)

        uploaded_file = get_object_or_404(UploadedFile, pk=file_id)
        reader = get_reader(uploaded_file)
        zipfile = ZipFile(reader)
        assets = _store_files(zipfile, user)
        content.file = create_new_version(content.file, user, comment='assets_package', shallow=True)
        update_content_assets(content, assets)
        content.stop_editing(user)
        content.save()
        send_import_confirmation(content, user)
    except BadZipfile:
        content.stop_editing(user)
        send_failure_confirmation(content, user, 'assets/not_zip_failure.txt')
    except Exception:
        import traceback
        content.stop_editing(user)
        logging.error("Error while importing assets package: %s", traceback.format_exc())
        mail_admins('Import assets package failed: content=%s, user=%s, package=%s' % (content_id, user_id, file_id), traceback.format_exc())
        send_failure_confirmation(content, user, 'assets/system_failure.txt')
    finally:
        if reader:
            reader.close()
        if zipfile:
            zipfile.close()
    return HttpResponse("OK")

def _read_mimetypes_from_file(data):
    result = {}
    errors = []

    for i, line in enumerate(data.splitlines()):
        try:
            splitted_value = line.split(',')
            file_name = splitted_value[0]
            mime_type = splitted_value[1]
            result[file_name] = mime_type.strip()
        except IndexError:
            errors.append('Error occured while reading mimetypes.txt [line: %s]' % i)

    return result, errors

def _store_files(zipfile, user):
    assets = []
    errors = []
    mimetypes_dict = {}

    file_name_list = zipfile.namelist()
    if 'mimetypes.txt' in file_name_list:
        data = zipfile.read('mimetypes.txt')
        mimetypes_dict, errors_from_read = _read_mimetypes_from_file(data)
        errors.extend(errors_from_read)
        file_name_list.remove('mimetypes.txt')

    for name in file_name_list:
        data = zipfile.read(name)

        if name in mimetypes_dict:
            mime_type = mimetypes_dict[name]
        else:
            try:
                mime_type = mimetypes.guess_type(name)[0]
            except Exception:
                errors.append('Could NOT guess mimetype of %s' % name)

        bucket = get_bucket_name('imported-resources')

        cleaned_name = name.replace(' ', '_')
        # GCS doesn't allow Unicode characters and characters like /, # or ?. So we're stripping name from all
        # non-alphanumeric characters except for . and _
        cleaned_name = re.sub('[^\w\.]+', '', cleaned_name)

        file_name = generate_unique_gcs_path(bucket, cleaned_name, user.id)
        store_file(file_name, mime_type, data)
        blob_key = blobstore.create_gs_key('/gs' + file_name)
        upfile = UploadedFile()
        upfile.filename = cleaned_name
        upfile.file = str(blob_key)
        upfile.content_type = mime_type
        upfile.owner = user
        upfile.path = file_name
        upfile.save()
        assets.append(upfile)
    return assets


def send_import_confirmation(content, user):
    subject = 'Lesson "%s" assets have been successfully updated' % content.title
    context = Context({'content': content, 'user': user, 'settings': settings})
    email = loader.get_template('assets/confirmation.txt')
    rendered = email.render(context)
    send_message(settings.SERVER_EMAIL, [user.email], subject, rendered)


def send_failure_confirmation(content, user, template):
    subject = 'Lesson "%s" assets have not been updated' % content.title
    context = Context({'content': content, 'user': user, 'settings': settings})
    email = loader.get_template(template)
    rendered = email.render(context)
    send_message(settings.SERVER_EMAIL, [user.email], subject, rendered)


@login_required
@user_passes_test(lambda user: user.is_superuser)
def replace(request):
    def render_response():
        return render(request, 'assets/replace.html')

    if request.method == "POST":
        space_id = request.POST['space']
        if not space_id:
            messages.error(request, 'Space ID must be provided!', 'danger')
            return render_response()

        space = get_object_or_none(Space, pk=space_id)
        if space is None:
            messages.error(request, 'Space with given ID does not exist', 'danger')
            return render_response()

        assets = request.POST['assets']

        validation_result = _validate_assets_replacement_data(assets)
        if not validation_result['is_valid']:
            messages.error(request, 'Invalid assets configuration: %s' % validation_result['message'], 'danger')
            return render_response()

        config = AssetsOrPagesReplacementConfig(
            user=request.user,
            space=space,
            meta_data=assets
        )
        config.save()

        trigger_backend_task('/assets/replace_async/%s' % config.id, target=get_versioned_module('download'),
                             queue_name='download')
        messages.success(request, 'Assets replacement task started. You will be notified via email when it completes.')

        # spaces = space.kids.filter(is_deleted=False)

    return render_response()

@login_required
@user_passes_test(lambda user: user.is_superuser)
def replace_page_names(request):
    def render_response():
        return render(request, 'assets/replace_page_names.html')

    if request.method == "POST":
        space_id = request.POST['space']
        if not space_id:
            messages.error(request, 'Space ID must be provided!', 'danger')
            return render_response()

        space = get_object_or_none(Space, pk=space_id)
        if space is None:
            messages.error(request, 'Space with given ID does not exist', 'danger')
            return render_response()

        prefix = request.POST['prefix']

        config = AssetsOrPagesReplacementConfig(
            user=request.user,
            space=space,
            meta_data=prefix
        )
        config.save()
        trigger_backend_task('/assets/replace_page_names_async/%s' % config.id, target=get_versioned_module('download'),
                             queue_name='download')
        messages.success(request, 'Pages titles replacement task started. You will be notified via email when it is completed.')

    return render_response()

def create_new_lesson(lesson, config):
    # Creating new version of lesson for possible failure cases (manual recreation if necessary)
    lesson.file = create_new_version(lesson.file, config.user)
    if lesson.file.history_for is None:
        lesson.file.history_for = lesson
        lesson.file.save()
    lesson.save()

@backend
def replace_page_names_async(_, config_id):
    config = get_object_or_404(AssetsOrPagesReplacementConfig, pk=config_id)
    prefix = config.meta_data
    log = {'edited': [], 'replaced': [], 'errors': []}

    lessons = list(Content.objects.filter(spaces=str(config.space.id)))
    for lesson in lessons:
        editor = lesson.who_is_editing()
        if editor is not None:
            log['edited'].append(lesson)
            continue

        create_new_lesson(lesson, config)

        lesson.set_user_is_editing(config.user)
        try:
            main_xml = xml.dom.minidom.parseString(lesson.file.contents)

            contents = lesson.file.contents
            replace_status, contents = replace_content_page_names(contents, main_xml, prefix)

            if replace_status:
                lesson.file.contents = contents
                lesson.file.save()
                log['replaced'].append(lesson)

        except Exception as ex:
            import traceback
            mail_admins("Exception in replacing titles", traceback.format_exc())
            log['errors'].append({
                'lesson': lesson,
                'message': ex.message,
                'traceback': traceback.format_exc()
            })
        lesson.stop_editing(config.user)

    subject = 'Titles replacement for space "%s" finished' % config.space.title
    _send_replacement_status_info(config, log, subject, 'assets/replace_page_names_status_info.txt')
    return HttpResponse()

@backend
def replace_async(_, config_id):
    config = get_object_or_404(AssetsOrPagesReplacementConfig, pk=config_id)
    assets = json.loads(config.meta_data)
    log = {'edited': [], 'replaced': [], 'omitted': [], 'errors': []}

    lessons = list(Content.objects.filter(spaces=str(config.space.id)).values('id'))
    for lesson_dict in lessons:
        lesson = Content.get_cached(id=lesson_dict['id'])
        editor = lesson.who_is_editing()

        if editor is not None:
            log['edited'].append(lesson)
            continue

        create_new_lesson(lesson, config)
        lesson.set_user_is_editing(config.user)

        try:
            status = _replace_assets_in_lesson(lesson, assets)
            if status:
                log['replaced'].append(lesson)
            else:
                log['omitted'].append(lesson)
        except Exception as ex:
            import traceback
            log['errors'].append({
                'lesson': lesson,
                'message': ex.message,
                'traceback': traceback.format_exc()
            })

        lesson.stop_editing(config.user)

    subject = 'Assets replacement for space "%s" finished' % config.space.title
    _send_replacement_status_info(config, log, subject, 'assets/replacement_status_info.txt')

    return HttpResponse()
