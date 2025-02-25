# -*- coding: utf-8 -*-
import json
import os
import re
import urllib.parse
import xml.dom.minidom
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden
from django.contrib import messages
from django.template import loader
from django.core.mail import mail_admins
from django.conf import settings
from django.db.models import Q
from libraries.utility.helpers import get_object_or_none, generate_unique_gcs_path
from lorepo.assets.models import AssetsOrPagesReplacementConfig
from lorepo.mycontent.models import Content
from lorepo.filestorage.forms import UploadForm
from lorepo.assets.util import (
    update_content_assets,
    update_asset_title,
    delete_asset,
    _validate_assets_replacement_data,
    _replace_assets_in_lesson,
    _send_replacement_status_info,
    replace_content_page_names,
)
from lorepo.permission.decorators import has_space_access
from lorepo.permission.models import Permission
from lorepo.filestorage.models import UploadedFile
from django.contrib.auth.models import User
from zipfile import ZipFile, BadZipfile
import mimetypes
import logging
from lorepo.filestorage.utils import get_reader, store_file, create_new_version
from lorepo.spaces.models import Space
from settings import get_bucket_name
from celery import shared_task

MAX_ASSETS_RETRIES = 10


@login_required
@has_space_access(Permission.ASSET_BROWSE)
def browse_assets(request, content_id):
    """
    View to browse assets associated with a content item.
    """
    content = get_object_or_404(Content, id=content_id)
    upload_url = "/assets/upload/{content_id}/".format(content_id=content_id)
    upload_package_url = "/assets/upload_package/{content_id}/".format(content_id=content_id)
    form = UploadForm()
    content_type = request.POST.get("type", None)
    assets = content.getAssets()
    available_types = set([asset.content_type for asset in assets])
    currently_edited = content.who_is_editing() is not None
    if currently_edited:
        messages.warning(request, "In order to upload a new asset, the lesson should not be opened in the editor.")
    if content_type is not None and content_type != "":
        assets = [asset for asset in assets if asset.content_type == content_type]
    return render(
        request,
        "assets/assets.html",
        {
            "content": content,
            "assets": assets,
            "upload_url": upload_url,
            "upload_package_url": upload_package_url,
            "form": form,
            "content_type": content_type,
            "available_types": sorted(available_types),
            "currently_edited": currently_edited,
        },
    )


@login_required
@has_space_access(Permission.ASSET_EDIT)
def rename_asset(request, content_id, href):
    """
    View to rename an asset.
    """
    content = get_object_or_404(Content, id=content_id)
    if request.method == "POST":
        user_editing = content.who_is_editing()
        if user_editing is not None:
            messages.warning(
                request,
                "Lesson is currently opened in editor by user <{user_editing}>, can't rename an asset.".format(
                    user_editing=user_editing
                ),
            )
            return HttpResponseRedirect("/assets/{content_id}/".format(content_id=content_id))
        update_asset_title(content, href, request.POST.get("title", ""))
        return HttpResponseRedirect("/assets/{content_id}/".format(content_id=content_id))
    else:
        assets = content.getAssets()
        asset = [asset for asset in assets if asset.href == href][0]
        return render(request, "assets/rename.html", {"asset": asset, "content": content})


@login_required
@has_space_access(Permission.ASSET_EDIT)
def upload_asset(request, content_id):
    """
    View to upload a new asset.
    """
    content = get_object_or_404(Content, id=content_id)
    if request.method == "POST":
        if len(request.FILES) > 0:
            user_editing = content.who_is_editing()
            if user_editing is not None:
                messages.warning(
                    request,
                    "Lesson is currently opened in editor by user <{user_editing}>, can't upload a new asset.".format(
                        user_editing=user_editing
                    ),
                )
                return HttpResponseRedirect("/assets/{content_id}/".format(content_id=content_id))
            form = UploadForm(request.POST, request.FILES)
            uploaded_file = form.save(False)
            uploaded_file.content_type = request.FILES["file"].content_type
            uploaded_file.filename = request.FILES["file"].name
            uploaded_file.owner = request.user
            uploaded_file.title = request.POST.get("title", "")
            uploaded_file.save()
            update_content_assets(content, uploaded_file)
    return HttpResponseRedirect("/assets/{content_id}/".format(content_id=content_id))


@login_required
@has_space_access(Permission.ASSET_REMOVE)
def delete_assets(request, content_id, href):
    """
    View to delete an asset.
    """
    content = get_object_or_404(Content, id=content_id)
    user_editing = content.who_is_editing()
    if user_editing is not None:
        messages.warning(
            request,
            "Lesson is currently opened in editor by user <{user_editing}>, can't delete an asset.".format(
                user_editing=user_editing
            ),
        )
        return HttpResponseRedirect("/assets/{content_id}/".format(content_id=content_id))
    delete_asset(content, href)
    return HttpResponseRedirect("/assets/{content_id}/".format(content_id=content_id))


@login_required
def upload_package(request, content_id):
    """
    View to upload a package of assets.
    """
    content = get_object_or_404(Content, id=content_id)
    if request.method == "POST":
        if len(request.FILES) > 0:
            form = UploadForm(request.POST, request.FILES)
            uploaded_file = form.save(False)
            uploaded_file.content_type = request.FILES["file"].content_type
            uploaded_file.filename = request.FILES["file"].name
            uploaded_file.owner = request.user
            uploaded_file.save()
            process_package_async.delay(content_id, uploaded_file.id, request.user.id)
            messages.info(
                request,
                "Your assets package will be imported in the background. You will be notified by email when it's finished.",
            )
    return HttpResponseRedirect("/assets/{content_id}/".format(content_id=content_id))


@shared_task
def process_package_async(content_id, file_id, user_id):
    """
    Celery task to process an uploaded assets package.
    """
    content = get_object_or_404(Content, id=content_id)
    user = get_object_or_404(User, id=user_id)
    reader = None
    zipfile = None

    try:
        if content.who_is_editing() is not None:
            retries = process_package_async.request.retries
            if retries > MAX_ASSETS_RETRIES:
                send_failure_confirmation(content, user, "assets/failure.txt")
                return "OK"
            else:
                raise Exception("Lesson is currently being edited.")
        content.set_user_is_editing(user)

        uploaded_file = get_object_or_404(UploadedFile, id=file_id)
        reader = get_reader(uploaded_file)
        zipfile = ZipFile(reader)
        assets = _store_files(zipfile, user)
        content.file = create_new_version(content.file, user, comment="assets_package", shallow=True)
        update_content_assets(content, assets)
        content.stop_editing(user)
        content.save()
        send_import_confirmation(content, user)
    except BadZipfile:
        content.stop_editing(user)
        send_failure_confirmation(content, user, "assets/not_zip_failure.txt")
    except Exception:
        import traceback
        content.stop_editing(user)
        logging.error("Error while importing assets package: %s", traceback.format_exc())
        mail_admins(
            "Import assets package failed: content={content_id}, user={user_id}, package={file_id}".format(
                content_id=content_id, user_id=user_id, file_id=file_id
            ),
            traceback.format_exc(),
        )
        send_failure_confirmation(content, user, "assets/system_failure.txt")
    finally:
        if reader:
            reader.close()
        if zipfile:
            zipfile.close()
    return "OK"


def _read_mimetypes_from_file(data):
    """
    Helper function to read mimetypes from a file.
    """
    result = {}
    errors = []

    for i, line in enumerate(data.splitlines()):
        try:
            splitted_value = line.split(",")
            file_name = splitted_value[0]
            mime_type = splitted_value[1]
            result[file_name] = mime_type.strip()
        except IndexError:
            errors.append("Error occurred while reading mimetypes.txt [line: {i}]".format(i=i))

    return result, errors


def _store_files(zipfile, user):
    """
    Helper function to store files from a zip package.
    """
    assets = []
    errors = []
    mimetypes_dict = {}

    file_name_list = zipfile.namelist()
    if "mimetypes.txt" in file_name_list:
        data = zipfile.read("mimetypes.txt").decode("utf-8")
        mimetypes_dict, errors_from_read = _read_mimetypes_from_file(data)
        errors.extend(errors_from_read)
        file_name_list.remove("mimetypes.txt")

    for name in file_name_list:
        data = zipfile.read(name)

        if name in mimetypes_dict:
            mime_type = mimetypes_dict[name]
        else:
            try:
                mime_type = mimetypes.guess_type(name)[0]
            except Exception:
                errors.append("Could NOT guess mimetype of {name}".format(name=name))

        bucket = get_bucket_name("imported-resources")

        cleaned_name = name.replace(" ", "_")
        # GCS doesn't allow Unicode characters and characters like /, # or ?. So we're stripping name from all
        # non-alphanumeric characters except for . and _
        cleaned_name = re.sub(r"[^\w\.]+", "", cleaned_name)

        file_name = generate_unique_gcs_path(bucket, cleaned_name, user.id)
        store_file(file_name, mime_type, data)
        upfile = UploadedFile()
        upfile.filename = cleaned_name
        upfile.file = file_name
        upfile.content_type = mime_type
        upfile.owner = user
        upfile.path = file_name
        upfile.save()
        assets.append(upfile)
    return assets


def send_import_confirmation(content, user):
    """
    Send a confirmation email after successfully importing assets.
    """
    subject = 'Lesson "{title}" assets have been successfully updated'.format(title=content.title)
    context = {"content": content, "user": user, "settings": settings}
    email = loader.get_template("assets/confirmation.txt")
    rendered = email.render(context)
    send_message(settings.SERVER_EMAIL, [user.email], subject, rendered)


def send_failure_confirmation(content, user, template):
    """
    Send a failure email if asset import fails.
    """
    subject = 'Lesson "{title}" assets have not been updated'.format(title=content.title)
    context = {"content": content, "user": user, "settings": settings}
    email = loader.get_template(template)
    rendered = email.render(context)
    send_message(settings.SERVER_EMAIL, [user.email], subject, rendered)


@login_required
@user_passes_test(lambda user: user.is_superuser)
def replace(request):
    """
    View to replace assets in a space.
    """
    def render_response():
        return render(request, "assets/replace.html")

    if request.method == "POST":
        space_id = request.POST["space"]
        if not space_id:
            messages.error(request, "Space ID must be provided!", "danger")
            return render_response()

        space = get_object_or_none(Space, id=space_id)
        if space is None:
            messages.error(request, "Space with given ID does not exist", "danger")
            return render_response()

        assets = request.POST["assets"]

        validation_result = _validate_assets_replacement_data(assets)
        if not validation_result["is_valid"]:
            messages.error(request, "Invalid assets configuration: {message}".format(message=validation_result["message"]), "danger")
            return render_response()

        config = AssetsOrPagesReplacementConfig(
            user=request.user,
            space=space,
            meta_data=assets,
        )
        config.save()

        replace_async.delay(config.id)
        messages.success(request, "Assets replacement task started. You will be notified via email when it completes.")

    return render_response()


@login_required
@user_passes_test(lambda user: user.is_superuser)
def replace_page_names(request):
    """
    View to replace page names in a space.
    """
    def render_response():
        return render(request, "assets/replace_page_names.html")

    if request.method == "POST":
        space_id = request.POST["space"]
        if not space_id:
            messages.error(request, "Space ID must be provided!", "danger")
            return render_response()

        space = get_object_or_none(Space, id=space_id)
        if space is None:
            messages.error(request, "Space with given ID does not exist", "danger")
            return render_response()

        prefix = request.POST["prefix"]

        config = AssetsOrPagesReplacementConfig(
            user=request.user,
            space=space,
            meta_data=prefix,
        )
        config.save()
        replace_page_names_async.delay(config.id)
        messages.success(request, "Pages titles replacement task started. You will be notified via email when it is completed.")

    return render_response()


@shared_task
def replace_page_names_async(config_id):
    """
    Celery task to replace page names in a space.
    """
    config = get_object_or_404(AssetsOrPagesReplacementConfig, id=config_id)
    prefix = config.meta_data
    log = {"edited": [], "replaced": [], "errors": []}

    lessons = list(Content.objects.filter(spaces=str(config.space.id)))
    for lesson in lessons:
        editor = lesson.who_is_editing()
        if editor is not None:
            log["edited"].append(lesson)
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
                log["replaced"].append(lesson)

        except Exception as ex:
            import traceback
            mail_admins("Exception in replacing titles", traceback.format_exc())
            log["errors"].append({
                "lesson": lesson,
                "message": str(ex),
                "traceback": traceback.format_exc(),
            })
        lesson.stop_editing(config.user)

    subject = 'Titles replacement for space "{title}" finished'.format(title=config.space.title)
    _send_replacement_status_info(config, log, subject, "assets/replace_page_names_status_info.txt")
    return "OK"


@shared_task
def replace_async(config_id):
    """
    Celery task to replace assets in a space.
    """
    config = get_object_or_404(AssetsOrPagesReplacementConfig, id=config_id)
    assets = json.loads(config.meta_data)
    log = {"edited": [], "replaced": [], "omitted": [], "errors": []}

    lessons = list(Content.objects.filter(spaces=str(config.space.id)).values("id"))
    for lesson_dict in lessons:
        lesson = get_object_or_404(Content, id=lesson_dict["id"])
        editor = lesson.who_is_editing()

        if editor is not None:
            log["edited"].append(lesson)
            continue

        create_new_lesson(lesson, config)
        lesson.set_user_is_editing(config.user)

        try:
            status = _replace_assets_in_lesson(lesson, assets)
            if status:
                log["replaced"].append(lesson)
            else:
                log["omitted"].append(lesson)
        except Exception as ex:
            import traceback
            log["errors"].append({
                "lesson": lesson,
                "message": str(ex),
                "traceback": traceback.format_exc(),
            })

        lesson.stop_editing(config.user)

    subject = 'Assets replacement for space "{title}" finished'.format(title=config.space.title)
    _send_replacement_status_info(config, log, subject, "assets/replacement_status_info.txt")

    return "OK"


def create_new_lesson(lesson, config):
    """
    Helper function to create a new version of a lesson.
    """
    lesson.file = create_new_version(lesson.file, config.user)
    if lesson.file.history_for is None:
        lesson.file.history_for = lesson
        lesson.file.save()
    lesson.save()