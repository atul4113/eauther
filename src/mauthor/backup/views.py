# -*- coding: utf-8 -*-
import json
import os
import re
import io
import xml.dom.minidom
from google.cloud import storage
from django.core.files.uploadedfile import UploadedFile
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse,\
    HttpResponseForbidden
from django.contrib import messages
from lorepo.spaces.models import Space, SpaceType
from lorepo.filestorage.models import UploadedFile, FileStorage
from lorepo.mycontent.util import get_contents_from_specific_space
from lorepo.filestorage.forms import UploadForm
from mauthor.backup.models import ProjectBackup, ExportedPackage
from xml.etree import ElementTree
from zipfile import ZipFile
from lorepo.corporate.signals import company_structure_changed
from lorepo.mycontent.models import Content
import datetime
from django.conf import settings
from django.template.context import Context
from django.template import loader
from lorepo.public.util import send_message
from django.contrib.auth.models import User
from lorepo.mycontent.service import add_content_to_space
from libraries.utility.queues import trigger_backend_task, delete_task
import logging
from django.core.mail import mail_admins
from lorepo.spaces.util import get_space_for_content
from lorepo.exchange.views import _zip_content
from lorepo.corporate.utils import get_division_for_space
from libraries.utility.helpers import get_object_or_none
from lorepo.spaces.service import update_space
from lorepo.permission.models import Permission
from lorepo.permission.decorators import has_space_access
from lorepo.filestorage.utils import get_reader, store_file_from_stream
from libraries.utility.environment import get_app_version, get_versioned_module
from mauthor.backup.utils import make_path, get_path
from mauthor.bulk.util import build_project_tree
from libraries.utility.decorators import backend
from settings import get_bucket_name


@login_required
@has_space_access(Permission.BACKUP_ADMIN)
def select_publications_for_backup(request, project_id):
    return build_project_tree(request, project_id, 'backup/select_publications.html')

@login_required
@has_space_access(Permission.BACKUP_ADMIN)
def backup_project(request, project_id):
    spaces = request.POST.getlist('spaces')
    resources = request.POST.getlist('resources', [])
    include_player = request.POST.get('include_player', 0)
    version = request.POST.get('version')

    payload = {
                'spaces' : spaces,
                'version': version,
                'include_player': include_player
              }

    if len(resources) > 0:
        payload.update({'resources' : resources})

    trigger_backend_task('/backup/%s/async/%s' % (project_id, request.user.id), payload=json.dumps(payload), target=get_versioned_module('backup'), queue_name='backup')
    messages.info(request, 'Lessons scheduled for backup. Once the backup is ready you will be notified via email.')
    return HttpResponseRedirect('/corporate/divisions')

@backend
def backup_project_async(request, project_id, user_id):
    try:
        payload = json.loads(request.body)
        project = get_object_or_404(Space, pk=project_id)

        if 'resources' not in payload:
            number_of_contents = 0
        else:
            contents = get_contents(project, payload.get('spaces', []))
            number_of_contents = len(contents)
        project_backup = ProjectBackup(number_of_contents=number_of_contents)
        project_backup.save()
        if number_of_contents > 0:
            version = payload.get('version')
            include_player = payload.get('include_player', 0)
            backup_resources(project_backup, contents, user_id, version, include_player)
        trigger_backend_task('/backup/structure/%s/%s/%s' % (project_id, project_backup.id, user_id), name='structure_%s' % project_backup.id, payload=request.body, target=get_versioned_module('backup'), queue_name='backup')
    except Exception:
        import traceback
        send_failure_notification(user_id, traceback.format_exc(), project.id)
    return HttpResponse('OK')

@backend
def send_notification(request, user_id, project_backup_id, project_id):
    project = get_object_or_none(Space, pk = project_id)
    project_backup = ProjectBackup.objects.get(pk=project_backup_id)
    exported_packages = ExportedPackage.objects.filter(project_backup=project_backup)
    user = User.objects.get(pk=user_id)
    context = Context({
        'project_backup': project_backup,
        'packages': exported_packages,
        'user': user,
        'project': project,
        'settings': settings
    })
    email = loader.get_template('backup/confirmation.txt')
    emails = [user.email]
    rendered = email.render(context)
    send_message(settings.SERVER_EMAIL, emails, "Backup created successfully", rendered)
    return HttpResponse("OK")

def get_contents(space, spaces_to_include):
    if str(space.id) not in spaces_to_include:
        return []
    contents = get_contents_from_specific_space(space.id, content_filter=lambda content: not content.is_deleted)
    for kid in space.kids.filter(is_deleted=False):
        tmp = get_contents(kid, spaces_to_include)
        contents.extend(tmp)
    return contents

def backup_resources(project_backup, contents, user_id, version, include_player):
    for content in contents:
        trigger_backend_task('/backup/export_lesson/%s/%s/%s/%s/%s' % (content.id, project_backup.id, user_id, version, include_player), target=get_versioned_module('backup'), queue_name='backup')

@backend
def backup_structure(request, project_id, project_backup_id, user_id):
    user = get_object_or_404(User, pk=user_id)
    try:
        project_backup = ProjectBackup.objects.get(pk=project_backup_id)
        if project_backup.number_of_contents > 0:
            exported_packages = ExportedPackage.objects.filter(project_backup=project_backup)
            exported_packages_contents = set([p.content_id for p in exported_packages])
            if len(exported_packages_contents) != project_backup.number_of_contents:
                return HttpResponseForbidden()
        else:
            exported_packages = []
        project = Space.objects.get(pk=project_id)
        payload = json.loads(request.body)
        file_name = _zip_project(project, payload.get('spaces', []), exported_packages)
        backup = _store_backup(file_name)
        project_backup = ProjectBackup.objects.get(pk=project_backup_id)
        project_backup.backup = backup
        project_backup.save()
        trigger_backend_task('/backup/notify/%s/%s/%s' % (project_backup.id, user.id, project.id), name='summary_%s' % project_backup.id, target=get_versioned_module(module_name = os.getenv('GAE_MODULE_NAME')), queue_name='backup')
    except Exception:
        import traceback
        send_failure_notification(user_id, traceback.format_exc(), project_id)
    return HttpResponse("OK")

def send_failure_notification(user_id, error_message = '', project_id = None):
    if project_id:
        project = Space.objects.get(pk = project_id)
    user = User.objects.get(pk=user_id)
    email = loader.get_template('backup/failure.txt')
    emails = [user.email]
    context = Context({ 'project_name' : project.title if project else '', 'username' : user.username })
    rendered = email.render(context)
    send_message(settings.SERVER_EMAIL, emails, "Backup was not created", rendered)
    logging.exception('Backup failed')

    mail_admins('Backup failed user_id=%s, project_id=%s' % (user.id, project_id), error_message)

def _zip_project(project, spaces_to_include, exported_packages):
    stream = io.StringIO()
    my_zip = ZipFile(stream, 'a')
    _backup_lessons(my_zip, project, spaces_to_include, exported_packages)
    return _save_zip(my_zip, stream, project.id)

def _backup_lessons(my_zip, project, spaces_to_include, exported_packages):
    project_xml = xml.dom.minidom.parseString("<project></project>")
    project_element = project_xml.getElementsByTagName('project')[0]
    project_element.setAttribute('title', project.title)
    _backup_lessons_from_space(my_zip, project, project_xml, project_element, spaces_to_include, exported_packages)
    my_zip.writestr('structure.xml'.encode('utf-8'), project_xml.toxml('utf-8'))


def _backup_lessons_from_space(my_zip, space, project_xml, xml_node, spaces_to_include, exported_packages):
    if str(space.id) not in spaces_to_include:
        return
    space_element = project_xml.createElement('space')
    space_element.setAttribute('title', space.title)
    space_element.setAttribute('id', str(space.id))
    space_element.setAttribute('rank', str(space.rank))
    xml_node.appendChild(space_element)
    contents = get_contents_from_specific_space(space.id, content_filter=lambda content: not content.is_deleted)
    for content in contents:
        content_element = project_xml.createElement('content')
        content_element.setAttribute('title', content.title)
        content_element.setAttribute('id', str(content.id))
        zip_for_content_list = [exported_package.zipped_content for exported_package in exported_packages if exported_package.content.id == content.id]
        if len(zip_for_content_list) > 0:
            zipped_content = zip_for_content_list[0]
            content_element.setAttribute('url', '%s/file/serve/%s' % (settings.BASE_URL, zipped_content.id))
        space_element.appendChild(content_element)
        path = make_path(content.id, content.title)
        _store_content_metadata(my_zip, path, content)
        file_name = path + "main.xml"
        my_zip.writestr(file_name, content.file.contents)
        for page in content.get_pages():
            file_name = path + str(page.id) + ".xml"
            my_zip.writestr(file_name, page.contents)
    for kid in space.kids.filter(is_deleted=False):
        _backup_lessons_from_space(my_zip, kid, project_xml, space_element, spaces_to_include, exported_packages)

def _store_content_metadata(my_zip, path, content):
    file_name = path + "metadata.xml"
    metadata = xml.dom.minidom.parseString("<metadata></metadata>")
    element = metadata.getElementsByTagName('metadata')[0]
    element.setAttribute("title", content.title)
    element.setAttribute("tags", content.tags)
    element.setAttribute("description", content.description)
    element.setAttribute("short_description", content.short_description)
    element.setAttribute("content_type", str(content.content_type))
    if content.icon_href:
        element.setAttribute("icon_href", content.icon_href)
    my_zip.writestr(file_name, metadata.toxml('utf-8'))

def _save_zip(my_zip, stream, unique_id):
    my_zip.close()
    bucket = get_bucket_name('export-packages')
    now = datetime.datetime.now()
    file_name = '%s/%s/%s/%s/%s/%s/%s/backup.zip' % (bucket, unique_id, now.year, now.month, now.day, now.hour, now.minute)
    store_file_from_stream(file_name, 'application/zip', stream)
    return file_name

def _store_backup(file_name, bucket_name='your_bucket_name', with_save=True):
    # Initialize a GCS client
    client = storage.Client()

    # Get the bucket object
    bucket = client.get_bucket(bucket_name)

    # Create a blob (file object) from the bucket
    blob = bucket.blob(file_name)

    # Upload the file to GCS
    # Assuming the file exists on local disk (you can replace this with your actual file object)
    with open(file_name, 'rb') as file:
        blob.upload_from_file(file)

    # Create an UploadedFile object to return
    upfile = UploadedFile()
    upfile.name = file_name
    upfile.file = blob
    upfile.content_type = 'application/zip'

    if with_save:
        upfile.save()  # This would save the object in your Django model or wherever it's required.

    return upfile

@backend
def export_lesson(request, content_id, project_backup_id, user_id, version, include_player):
    try:
        project_backup = ProjectBackup.objects.get(pk=project_backup_id)
        content = Content.get_cached(id=content_id)
        if ExportedPackage.objects.filter(project_backup=project_backup, content=content).count():
            logging.info('Duplicated lesson export!')
            return HttpResponse("Duplicated")
        file_name = _zip_content(content, user_id, version, include_player=include_player)
        upfile = UploadedFile()
        upfile.file = str(blobstore.create_gs_key('/gs' + file_name))
        upfile.path = file_name
        upfile.content_type = 'application/zip'
        upfile.save()
        exported_lesson = ExportedPackage(zipped_content=upfile, project_backup=project_backup, content=content)
        exported_lesson.save()
    except Exception:
        import traceback
        delete_task("summary_%s" % project_backup_id, queue_name='backup')
        delete_task("structure_%s" % project_backup_id, queue_name='backup')
        space = get_space_for_content(content)
        project = get_division_for_space(space)
        send_failure_notification(user_id, traceback.format_exc(), project.id)
    return HttpResponse("OK")

@login_required
@has_space_access(Permission.BACKUP_ADMIN)
def restore_project(request):
    upload_url = blobstore.create_upload_url(request.path)
    next_url = request.REQUEST['next'] if 'next' in request.REQUEST else '/mycontent'
    form = UploadForm()

    if request.method == 'POST':
        if len(request.FILES) > 0:
            form = UploadForm(request.POST, request.FILES)
            uploaded_file = form.save(False)
            uploaded_file.save()
            trigger_backend_task('/backup/restore/%s/%s/%s' % (request.user.id, request.user.company.id, uploaded_file.id), target=get_versioned_module('backup'), queue_name='backup')
            messages.info(request, 'Project will be restored in background. Once it is restored you will be notified by email.')
            return HttpResponseRedirect(next_url)
        else:
            messages.warning(request, 'You need to select file with project backup.')

    return render(request, 'backup/restore.html', {'upload_url' : upload_url, 'form' : form, 'next' : next_url})

@backend
def restore_project_async(request, user_id, company_id, uploaded_file_id):
    user = User.objects.get(pk=user_id)
    errors = []
    project_name = ''
    try:
        company = Space.objects.get(pk=company_id)
        uploaded_file = UploadedFile.objects.get(pk=uploaded_file_id)
        reader = get_reader(uploaded_file)
        my_zip = ZipFile(reader)
        structure = my_zip.read('structure.xml')
        structure_xml = ElementTree.fromstring(structure)
        project_name = structure_xml[0].attrib['title'] if 'title' in structure_xml[0].attrib else ''
        mappings = _recreate_structure(company, structure_xml)
        errors = _recreate_contents(user, my_zip, structure_xml, mappings)
        company_structure_changed.send(None, company_id=company.id, user_id=user_id)
        if len(errors) > 0:
            raise Exception
        email = loader.get_template('backup/restore_confirmation.txt')
        emails = [user.email]
        rendered = email.render(Context({ 'user' : user, 'project' : project_name }))
        send_message(settings.SERVER_EMAIL, emails, "Backup restored successfully", rendered)
    except Exception:
        import traceback
        email = loader.get_template('backup/restore_failure.txt')
        emails = [user.email]
        rendered = email.render(Context({ 'username' : user.username, 'project_name' : project_name, 'errors' : errors }))
        send_message(settings.SERVER_EMAIL, emails, "Backup was not restored", rendered)
        logging.exception('Restore project failed')
        mail_admins('Restore project failed user_id=%s, company_id=%s' % (user_id, company_id), traceback.format_exc())
    return HttpResponse('OK')

def _recreate_structure(company, structure_xml):
    mappings = {}
    for element in structure_xml:
        if element.tag == 'space':
            _recreate_space(company, element, 'Restored: ', mappings)
    return mappings

def _recreate_space(parent, element, name_prefix, mappings):
    old_id = element.attrib['id']
    old_name = element.attrib['title']
    old_rank = element.attrib['rank'] if 'rank' in element.attrib else 20
    space = Space( title = name_prefix + old_name, parent = parent, space_type = SpaceType.CORPORATE, rank = int(old_rank) )
    update_space(space)
    mappings[old_id] = space
    for child in element:
        if child.tag == 'space':
            _recreate_space(space, child, '', mappings)

def _recreate_contents(user, my_zip, structure_xml, mappings):
    errors = []
    for project in structure_xml:
        errors.extend(_recreate_contents_in_space(user, my_zip, project, mappings))
    return errors

def _recreate_contents_in_space(user, my_zip, space_element, mappings):
    old_id = space_element.attrib['id']
    space = mappings[old_id]
    errors = []
    for child in space_element:
        if child.tag == 'content':
            try:
                _recreate_content(user, my_zip, child, space)
            except Exception:
                import traceback
                logging.exception('Restore project failed')
                content_id = child.attrib['id']
                content_title = child.attrib['title']
                mail_admins('Restore project failed user_id=%s, content=[%s] %s' % (user.id, content_id, content_title), traceback.format_exc())
                errors.append('[%s] %s' % (content_id, content_title))
        elif child.tag == 'space':
            errors.extend(_recreate_contents_in_space(user, my_zip, child, mappings))
    return errors

def _recreate_content(user, my_zip, child, space):
    old_id = child.attrib['id']
    title = child.attrib['title']
    path = get_path(my_zip, old_id, title)
    content = _create_content(user, my_zip, path)
    mappings = _create_pages(user, my_zip, path)
    main_file = _create_main_file(user, my_zip, path, mappings)
    content.file = main_file
    content.save()
    main_file.history_for = content
    main_file.save()
    add_content_to_space(content, space)

def _create_content(user, my_zip, path):
    metadata_bytes = my_zip.read(path + 'metadata.xml')
    metadata = ElementTree.fromstring(metadata_bytes)
    now = datetime.datetime.now()
    content = Content(
        title=metadata.attrib['title'], 
        tags=metadata.attrib['tags'], 
        description=metadata.attrib['description'], 
        short_description=metadata.attrib['short_description'], 
        content_type=metadata.attrib['content_type'],
        created_date=now, 
        modified_date=now, 
        author=user)
    if 'icon_href' in metadata.attrib:
        content.icon_href = metadata.attrib['icon_href']
    return content

def _create_pages(user, my_zip, path):
    mappings = {}
    now = datetime.datetime.now()
    for name in my_zip.namelist():
        match = re.match('%s(?P<page_id>\d+).xml' % re.escape(path), name)
        if match:
            data = my_zip.read(name)
            page = FileStorage(
                            created_date = now,
                            modified_date = now,
                            content_type = "text/xml",
                            contents = data,
                            owner = user)
            page.save()
            mappings[match.group('page_id')] = page.id
    return mappings

def _create_main_file(user, my_zip, path, mappings):
    now = datetime.datetime.now()
    data = my_zip.read('%smain.xml' % path)
    doc = xml.dom.minidom.parseString(data)
    for page in doc.getElementsByTagName('page'):
        if page.getAttribute('href') in mappings:
            page.setAttribute('href', str(mappings[page.getAttribute('href')]))

    main_file = FileStorage(
                            created_date = now,
                            modified_date = now,
                            content_type = "text/xml",
                            contents = doc.toxml("utf-8"),
                            owner = user,
                            version = 1)
    main_file.save()
    return main_file