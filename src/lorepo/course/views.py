import os
from google.api_core.exceptions import TooManyRequests, DeadlineExceeded
from django.shortcuts import render
from src.lorepo.exchange.utils import RETRY_ERRORS
from src.lorepo.spaces.models import Space
from src.lorepo.mycontent.util import get_contents_from_specific_space
from src.libraries.utility.helpers import get_object_or_none, generate_unique_gcs_path
from django.http import HttpResponse, HttpResponseRedirect,\
    HttpResponseForbidden
from django.template import loader
from django.template.context import Context
from src.lorepo.course.models import Course, ExportedCourse, ExportedCourseLesson, LessonAlreadyCreatedError
from django.contrib import messages
from src.lorepo.filestorage.models import FileStorage, UploadedFile
import datetime
from src.libraries.utility.redirect import get_redirect, get_redirect_url,\
    join_redirect_urls, get_redirect_urls
from src.lorepo.course.helpers import parse_serialized_toc, \
    get_ebook_resources_node, remove_unrelated_resources, check_deleted_lessons
import logging
from src.lorepo.mycontent.models import Content, ContentType
import json
from src.lorepo.exchange.views import _zip_content
from src.libraries.utility.queues import delete_task, trigger_backend_task
from src.libraries.utility.environment import get_versioned_module
from zipfile import ZipFile, ZIP_DEFLATED
from django.contrib.auth.models import User
from src.lorepo.public.util import send_message
from src.mauthor.utility.utils import sanitize_title
from src import settings
from src.mauthor.backup.views import _store_backup
from django.core.mail import mail_admins
from django.contrib.auth.decorators import login_required
from src.lorepo.permission.decorators import has_space_access
from src.lorepo.permission.models import Permission
import src.libraries.utility.cacheproxy as cache
from xml.dom import minidom
from src.lorepo.course.scorm import store_scorm_manifest
from src.lorepo.spaces.util import load_kids, structure_as_dict
from src.libraries.utility.decorators import backend
from src.lorepo.token.decorators import form_token, set_form_token


@login_required
@has_space_access(Permission.COURSE_MANAGE)
def courses_list(request, project_id):
    project = Space.objects.get(pk=project_id)
    order = request.GET.get('order', 'ASC')
    if order == 'ASC':
        order_param = 'name'
    else:
        order_param = '-name'
    courses = Course.objects.filter(project=project).order_by(order_param)
    now = datetime.datetime.now()

    if request.method == 'POST':
        name = request.POST['name']
        if name == '':
            messages.error(request, 'Name can NOT be empty!')
        else:
            context = Context({'name': name})
            structure_xml = FileStorage(
                created_date=now,
                modified_date=now,
                owner=request.user,
                contents=loader.get_template('initdata/course/root.xml').render(context).encode('utf-8'),
                content_type='application/xml')
            structure_xml.save()
            course = Course(name=name, project=project, structure_xml=structure_xml)
            course.save()
            return HttpResponseRedirect('/course/list/%s' % project_id)
    return render(request, 'course/index.html', {
        'courses': courses,
        'project': project,
        'order': order
    })


@login_required
@has_space_access(Permission.COURSE_MANAGE)
def rename(request, course_id):
    course = Course.objects.get(pk=course_id)
    if request.method == 'POST':
        course.name = request.POST.get('name', course.name)
        course.save()
        return get_redirect(request)
    return render(request, 'course/rename_course.html', {'course': course, 'next': get_redirect_url(request)})


@login_required
@has_space_access(Permission.COURSE_MANAGE)
def remove(request, course_id):
    course = Course.objects.get(pk = course_id)
    course.delete()
    return get_redirect(request)


def _check_has_lessons(spaces):
    for space in spaces:
        space.has_lessons = Content.objects.filter(spaces=str(space.id), is_deleted=False).count() > 0
        _check_has_lessons(space.kids.filter(is_deleted=False))


def _filter_publications(publications):
    return [pub for pub in publications if pub.kids.filter(is_deleted=False).count() > 0 or pub.contents_count > 0]


def get_kids(_, publication_id):
    publication = Space.objects.get(pk=publication_id)
    template = loader.get_template('course/kids.json')

    load_kids([publication], recursive=False)
    for kid in publication.loaded_kids:
        kid.has_kids = kid.kids.filter(is_deleted=False).count() > 0
        kid.has_lessons = kid.contents_count > 0
        kid.title = sanitize_title(kid.title)

    context = Context({'kids': publication.loaded_kids})
    json_string = template.render(context)

    return HttpResponse(content=json_string)


def _set_opened_toc(chapters, cached_opened_toc):
    for chapter in chapters:
        chapter['open'] = chapter['node_id'] in cached_opened_toc
        if len(chapter['kids']) > 0:
            _set_opened_toc(chapter['kids'], cached_opened_toc)


def _set_opened_al(publications, cached_opened_al):
    for publication in publications:
        if str(publication.pk) in cached_opened_al:
            publication.open = True
            kids = publication.kids.filter(is_deleted=False)
            publication.lessons = get_contents_from_specific_space(publication, 
                                                                   content_filter=lambda c: not c.is_deleted and c.content_type != ContentType.ADDON)
            if kids.count() > 0:
                _set_opened_al(kids, cached_opened_al)
                publication.loaded_kids = kids
        else:
            publication.open = False


@login_required
@has_space_access(Permission.COURSE_MANAGE)
def edit_table_of_contents(request, course_id, project_id):
    course = Course.get_cached_course(course_id)

    try:
        if course.is_being_exported:
            messages.info(request, 'You cannot edit. Wait until exported course is ready.', 'danger')
            return get_redirect(request)
    except AttributeError:
        pass

    chapters = course.get_structure()
    project = Space.objects.get(pk=project_id)
    publications = project.kids.filter(is_deleted=False).order_by('title')
    publications = _filter_publications(publications)
    ebooks = course.get_eBooks()

    key_pattern = 'course_toc_%(user_id)s_%(course_id)s'
    key = key_pattern % {'user_id': request.user.id, 'course_id': course_id}
    cached_opened_toc = cache.get(key)
    if cached_opened_toc:
        _set_opened_toc(chapters, cached_opened_toc)

    key_pattern = 'course_al_%(user_id)s_%(course_id)s'
    key = key_pattern % {'user_id': request.user.id, 'course_id': course_id}
    cached_opened_al = cache.get(key)
    if cached_opened_al:
        _set_opened_al(publications, cached_opened_al)

    lessons_in_trash = check_deleted_lessons(course)
    if lessons_in_trash:
        messages.error(request, 'Course with lessons in Trash cannot be exported.', 'danger')

    return render(request, 'course/edit_table_of_contents.html', {
        'course': course,
        'back_url': get_redirect_url(request),
        'chapters': chapters,
        'project_id': project_id,
        'publications': publications,
        'eBooks': ebooks,
        'lessons_in_trash': lessons_in_trash
    })


def save_table_of_contents(request, course_id):
    course = Course.objects.get(pk = course_id)
    table_of_contents = parse_serialized_toc(request.POST['toc'])
    lessons = request.POST['lessons']
    eBooks = request.POST['eBooks']
    ebooks = json.loads(eBooks)
    for ebook in ebooks:
        ebook['resources'] = get_ebook_resources_node(minidom.parseString(course.structure_xml.contents), ebook['id'])
    course.save_structure(table_of_contents, json.loads(lessons), ebooks)
    return HttpResponse()


def get_publication_lessons(_, publication_id):
    publication = get_object_or_none(Space, pk=publication_id)
    json_string = ''

    if publication:
        lessons = get_contents_from_specific_space(publication.id, content_filter = lambda c: c.is_deleted == False and c.content_type != ContentType.ADDON)
        for lesson in lessons:
            lesson.title = sanitize_title(lesson.title)

        template = loader.get_template('course/lessons.json')
        context = Context({ 'lessons' : lessons })
        json_string = template.render(context)

    return HttpResponse(content = json_string)


def _get_lessons(request):
    lessons_list = request.POST.getlist('lessons[]')
    lessons = []
    for lesson in lessons_list:
        lessons_dict = {}
        splitted = lesson.split('|')
        lessons_dict['id'] = splitted[0]
        lessons_dict['name'] = splitted[1]
        content = Content.get_cached_or_none(id=lessons_dict['id'])
        if content:
            lessons_dict['version'] = str(content.file.version)
        else:
            lessons_dict['version'] = '0'
        lessons.append(lessons_dict)
    return lessons


def add_lesson(request, chapter_id, course_id):
    course = Course.objects.get(pk=course_id)
    lessons = _get_lessons(request)
    success = course.add_lessons_to_chapter(lessons, chapter_id)
    if success:
        return HttpResponse()
    else:
        return HttpResponse('ChapterNotFound')


def add_lesson_to_eBook(request, course_id):
    course = Course.objects.get(pk=course_id)
    eBooks = _get_lessons(request)
    course.add_eBooks(eBooks)
    return HttpResponse()


def remove_lessons(request, course_id):
    course = Course.objects.get(pk = course_id)
    course.remove_lessons(request.POST.getlist('lessons[]'))
    course.remove_eBooks(request.POST.getlist('eBooks[]'))
    return HttpResponse()


@login_required
@has_space_access(Permission.COURSE_MANAGE)
def get_space(request, course_id, space_id):
    space = Space.objects.get(pk=space_id)
    structure_dict = structure_as_dict(space)
    return HttpResponse(json.dumps(structure_dict))


@login_required
@has_space_access(Permission.COURSE_MANAGE)
def remove_chapter(request, chapter_id, course_id):
    course = Course.objects.get(pk=course_id)
    course.remove_chapter(chapter_id)
    course.save()
    return get_redirect(request)


@form_token('export')
@login_required
@has_space_access(Permission.COURSE_MANAGE)
def trigger_export(request, course_id):
    course = Course.get_cached_course(course_id)
    if course.is_being_exported:
        messages.warning(request, 'Course is being exported.')
        return get_redirect(request)

    if check_deleted_lessons(course):
        messages.error(request, 'Course has deleted lessons. Please remove them from Table of Contents.', 'danger')
        return HttpResponseRedirect('/course/edit_table_of_contents/%s/%s?next=%s' % (course.id, course.project_id, get_redirect_url(request)))

    if request.method == 'POST':
        set_form_token(request.user, 'export')
        version = request.POST.get('scorm_version', 2)
        include_player = request.POST.get('include_player', 0)
        course.is_being_exported = True
        course.save()
        try:
            trigger_backend_task('/course/export/%s/async/%s/%s/%s' % (course_id, request.user.id, version, include_player), target=get_versioned_module('backup'), queue_name='backup')
        except Exception as e:
            course.is_being_exported = False
            course.save()
            raise e

        messages.info(request, 'Course scheduled for export. Once the exported course is ready you will be notified via email.')
        return get_redirect(request)
    else:
        return render(request, 'course/export.html', {
            'next_url': get_redirect_url(request),
            'course_id': course_id
        })


@backend
def export(_, course_id, user_id, version, include_player):

    def report_error():
        logging.exception("Course export failed, course_id=%s, user_id=%s", course_id, user_id)
        send_failure_notification(course_id, user_id)

    try:
        course = Course.objects.get(pk=course_id)
        course.set_id()
        lessons_ids = set(course.get_lessons_ids())
        eBooks_ids = set(course.get_eBooks_ids())
        lessons_ids.update(eBooks_ids)
        course.update_lessons(lessons_ids)
        course.update_ebooks(eBooks_ids)
        exported_course = ExportedCourse(number_of_contents = len(lessons_ids), course = course)
        exported_course.save()

        for content_id in lessons_ids:
            url = '/course/export_lesson/%s/%s/%s/%s/%s' % (content_id, user_id, exported_course.pk, version, include_player)
            name = url.replace('/', '_')
            trigger_backend_task(url, name=name, target=get_versioned_module(os.environ('module_name')), queue_name='backup')

        trigger_backend_task('/course/export_structure/%s/%s/%s/%s' %
                                 (course_id, exported_course.pk, user_id, version), name="structure_export_course_%s" % exported_course.pk, target=get_versioned_module(get_current_module_name()), queue_name='backup')

    except DeadlineExceeded:
        report_error()
        try:
            course.is_being_exported = False
            course.save()
        except Exception:
            pass
    except Exception:
        report_error()

    return HttpResponse()


def _store_lessons(my_zip, exported_course_lessons, user_id):
    for ecl in exported_course_lessons:
        # create only folders for the lesson
        my_zip.writestr(str(ecl.content.id) + "/", "")


@backend
def export_structure(request, course_id, exported_course_id, user_id, version):
    exception_raised = False

    course = Course.get_cached_course(course_id)

    try:
        exported_course = ExportedCourse.objects.get(pk=exported_course_id)
        exported_course_lessons = ExportedCourseLesson.objects.filter(exported_course=exported_course)
        if len(exported_course_lessons) != exported_course.number_of_contents:
            return HttpResponseForbidden()

        bucket = settings.get_bucket_name('export-packages')
        file_name = generate_unique_gcs_path(bucket, 'course.zip', user_id, course_id)
        generate_gcs_zip(course, exported_course_lessons, file_name, user_id, version)
    except Exception:
        exception_raised = True

    try:
        store_gcs_file_data(file_name, exported_course)
    except Exception:
        exception_raised = True

    if exception_raised:
        send_failure_notification(course_id, user_id)
    else:
        send_notification(request, user_id, exported_course_id)

    course.is_being_exported = False
    course.save()

    return HttpResponse()


from google.cloud import storage
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.http import HttpResponse, HttpResponseForbidden
import logging
from .models import ExportedCourse, Content, ExportedCourseLesson, UploadedFile, Course
from .exceptions import RETRY_ERRORS, LessonAlreadyCreatedError
from .utils import _zip_content, send_failure_notification, delete_task


@backend
def export_lesson(_, content_id, user_id, exported_course_id, version, include_player):
    try:
        upfile = None
        exported_course = ExportedCourse.objects.get(pk=exported_course_id)
        content = Content.get_cached(id=content_id)
        exported_course.validate_lesson_created(content)

        # Create the zipped content file
        file_name = _zip_content(content, user_id, version, include_player=include_player)

        # Upload the file to Google Cloud Storage (GCS)
        storage_client = storage.Client()
        bucket = storage_client.get_bucket('your-bucket-name')  # Replace with your GCS bucket name
        blob = bucket.blob(file_name)

        # Open and upload the file (assuming it's a zip file)
        with open(file_name, 'rb') as f:
            blob.upload_from_file(f, content_type='application/zip')

        # After uploading, create the UploadedFile object and save it
        upfile = UploadedFile()
        upfile.file = file_name  # or store the GCS URL (blob.public_url)
        upfile.path = file_name
        upfile.content_type = 'application/zip'
        upfile.save()

        # Validate and create the ExportedCourseLesson
        exported_course.validate_lesson_created(content)
        exported_course_lesson = ExportedCourseLesson(exported_course=exported_course, zipped_content=upfile,
                                                      content=content)
        exported_course_lesson.save()

    except RETRY_ERRORS as e:
        logging.exception(
            '%s - retrying. If you see too much of these, you will need to investigate' % type(e).__name__)
        return HttpResponseForbidden()
    except LessonAlreadyCreatedError as e:
        logging.error(e)
        if upfile:
            upfile.delete()
        return HttpResponse('LessonAlreadyCreatedError')
    except Exception:
        delete_task("structure_export_course_%s" % exported_course_id, queue_name='backup')
        course_id = exported_course.course.id
        send_failure_notification(course_id, user_id, content_id)
        course = Course.objects.get(pk=course_id)
        course.is_being_exported = False
        course.save()

    return HttpResponse()


def send_failure_notification(course_id, user_id, content_id=None):
    course = Course.objects.get(pk = course_id)
    user = User.objects.get(pk = user_id)
    email = loader.get_template('course/failure.txt')
    emails = [user.email]
    context = Context({ 'course' : course, 'username' : user.username })
    rendered = email.render(context)
    send_message(settings.SERVER_EMAIL, emails, 'Export Course Failed"%s"' % course.name, rendered)
    logging.exception('Course Export failed')
    import traceback
    if not course_id is None:
        mail_admins('Course Export failed user_id=%s, course_id=%s, content_id=%s' % (user.pk, course.pk, content_id), traceback.format_exc())
    else:
        mail_admins('Course Export failed user_id=%s, course_id=%s' % (user.pk, course.pk), traceback.format_exc())


def send_notification(_, user_id, exported_course_id):
    exported_course = ExportedCourse.objects.get(pk = exported_course_id)
    exported_lessons = ExportedCourseLesson.objects.filter(exported_course = exported_course)
    user = User.objects.get(pk=user_id)
    import base64
    context = Context({
        'exported_course': exported_course,
        'exported_lessons': exported_lessons,
        'user': user,
        'course_code': base64.b64encode(exported_course.uploaded_file.path),
        'settings': settings
    })
    email = loader.get_template('course/confirmation.txt')
    emails = [user.email]
    rendered = email.render(context)
    send_message(settings.SERVER_EMAIL, emails, "Course Exported Successfully", rendered)
    return HttpResponse()


def _set_cached(key, structure_state, node_id):
    timeout = 60 * 15
    cached = cache.get(key)
    if cached:
        if structure_state == 'open' and node_id not in cached:
            cached.append(node_id)
            cache.set(key, cached, timeout)
        elif structure_state == 'close' and node_id in cached:
            cached.remove(node_id)
            cache.set(key, cached, timeout)
    elif structure_state == 'open':
        cache.set(key, [node_id], timeout)


def set_structure_state(request):
    course_id = request.POST.get('course_id')
    node_id = request.POST.get('node_id')
    structure_state = request.POST.get('structure_state')
    cache_key_prefix = request.POST.get('cache_key_prefix')

    key_pattern = '%(cache_key_prefix)s_%(user_id)s_%(course_id)s'
    key = key_pattern % { 'user_id' : request.user.id, 'course_id' : course_id, 'cache_key_prefix' : cache_key_prefix }
    _set_cached(key, structure_state, node_id)

    return HttpResponse()


def render_player(request, content_id):
    logging.info('render_player')
    content = Content.get_cached(id = content_id)
    return render(request, 'course/render_player.html', { 'eBook' : content })


def save_resources(request):
    course_id = request.POST.get('course_id')
    eBook_id = request.POST.get('eBook_id')
    page_index = request.POST.get('page_index')
    course = Course.objects.get(pk = course_id)
    ids_to_add = request.POST.getlist('ids_to_add[]')
    ids_to_remove = request.POST.getlist('ids_to_remove[]')
    course.edit_resources(eBook_id, page_index, ids_to_add, ids_to_remove)
    return HttpResponse()


def get_resources(_, course_id, content_id, page_index):
    content = Content.get_cached(id = content_id)
    course = Course.objects.get(pk = course_id)
    return HttpResponse(json.dumps(course.get_resources(content.id, page_index)))


def edit_resources(request, course_id, content_id):
    content = Content.get_cached(id = content_id)
    course = Course.objects.get(pk = course_id)
    return render(request, 'course/edit_resources.html', { 
                  'eBook' : content,
                  'chapters' : course.get_structure(),
                  'course' : course,
                  'project_id' : '',
                  'back_url' : join_redirect_urls(get_redirect_urls(request))
                   })


def edit_resources_iframe(request, content_id):
    content = Content.get_cached(id = content_id)
    return render(request, 'course/edit_resources_iframe.html', {
                  'content' : content,
                   })


def generate_gcs_zip(course, exported_course_lessons, file_name, user_id, version):
    my_zip = None
    my_file = None

    try:
        with open(file_name, 'rb') as my_file:
            my_zip = ZipFile(my_file, 'w', ZIP_DEFLATED)

            course.save_exported_lessons(exported_course_lessons)
            course_xml = course.structure_xml.contents
            course_xml = remove_unrelated_resources(course_xml)
            my_zip.writestr('structure.xml'.encode('utf-8'), course_xml)
            store_scorm_manifest(my_zip, course, version)
            _store_lessons(my_zip, exported_course_lessons, user_id)
    except Exception as e:
        raise e
    finally:
        if my_zip is not None:
            my_zip.close()
        if my_file is not None:
            my_file.close()


def store_gcs_file_data(file_name, exported_course):
    try:
        upfile = _store_backup(file_name)
        exported_course.uploaded_file = upfile
        exported_course.save()
    except Exception as e:
        raise e
