from django.core.mail import mail_admins, send_mail
from django.template.defaultfilters import filesizeformat
from django.http import HttpResponse
import cloudstorage as gcs
from libraries.utility.cursors import get_cursor, set_cursor
from lorepo.corporate.models import CompanyUser
from lorepo.course.models import Course, ExportedCourse, ExportedCourseLesson
import datetime
from libraries.utility.decorators import backend, cron_method
from lorepo.filestorage.utils import open_file
import unicodedata
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from libraries.utility.queues import trigger_backend_task
import logging
import traceback
from lorepo.spaces.util import  get_spaces_tree, is_space_owner
from lorepo.spaces.models import Space, SpaceAccess, LockedSpaceAccess, SpaceType
from lorepo.corporate.signals import company_structure_changed
from mauthor.company.util import get_company_properties
from django.contrib.auth.models import User
from datetime import date
from django.template.loader import render_to_string
from settings import SERVER_EMAIL
from lorepo.public.util import send_message
from settings import get_bucket_name


def keepalive(request):
    return HttpResponse("ok")


# cron for deleting old exported courses
@cron_method
def delete_old_courses_cron(_):
    logging.info('[delete_old_courses] delete_old_courses_cron start')
    _delete_old_courses()
    logging.info('[delete_old_courses] delete_old_courses_cron end')
    return HttpResponse('ok')

def _delete_old_courses():
    url = '/cron/delete_old_courses_async'
    trigger_backend_task(url)

@login_required
@user_passes_test(lambda user: user.is_superuser, '/', '')
def delete_old_courses(request):
    _delete_old_courses()
    return HttpResponse('ok')

@backend
def delete_old_courses_async(_):
    now = datetime.datetime.now()

    delete_date = now - datetime.timedelta(weeks=8)

    all_exported_courses = ExportedCourse.objects.filter(
        created_date__lte=delete_date
    )

    course_page_size = 30
    lesson_page_size = 30
    total_size = 0
    deleted_courses = 0
    deleted_lessons = 0

    log_file_name = '%s/0000_deleted_courses_logs/%s_%s_%s.txt' % (get_bucket_name('export-packages'), now.year, now.month, now.day)

    with open_file(log_file_name, 'text/plain') as my_file:
        
        course_results = all_exported_courses[:course_page_size]
        try:
            
            while len(course_results) > 0:
                course_db_cursor = get_cursor(course_results)
    
                for exported_course in course_results:
                    try:
                        does_exist = exported_course.course
                        normalized_log = unicodedata.normalize('NFKD', 'Course id: %s | Course name: %s | Exported course id: %s | Created date: %s\n' % (exported_course.course.id, exported_course.course.name, exported_course.id, exported_course.course.created_date)).encode('ascii','ignore')
                    except Course.DoesNotExist:
                        normalized_log = unicodedata.normalize('NFKD', 'Course id: %s | Course does not exist' % (exported_course.course_id)).encode('ascii','ignore')

                    my_file.write(normalized_log)

                    exported_course_lessons = ExportedCourseLesson.objects.filter(exported_course = exported_course)
                    lesson_results = exported_course_lessons[:lesson_page_size]
                    if len(lesson_results) > 0:
                        normalized_log = unicodedata.normalize('NFKD', '\tLessons:\tSize\t\tContent ID\t\tCreated date\n').encode('ascii','ignore')
                        my_file.write(normalized_log)

                    while len(lesson_results) > 0:
                        lesson_db_cursor = get_cursor(lesson_results)
                        for exported_lesson in lesson_results:
                            blobstore_info = exported_lesson.zipped_content.file.file.blobstore_info

                            if blobstore_info is not None:
                                size = blobstore_info.size
                            else:
                                try:
                                    size = gcs.stat(exported_lesson.zipped_content.path).st_size
                                except gcs.NotFoundError:
                                    size = 0

                            log = filesizeformat(size)+ '\t\t' + str(exported_lesson.content.id) + '\t' + str(exported_lesson.created_date)

                            normalized_log = unicodedata.normalize('NFKD', '\t\t\t%s\n' % (log)).encode('ascii','ignore')
                            my_file.write(normalized_log)
                            if exported_lesson.zipped_content is not None:
                                exported_lesson.zipped_content.delete()
                            exported_lesson.delete()
                            total_size = total_size + size
                            deleted_lessons = deleted_lessons + 1

                        lesson_results = set_cursor(exported_course_lessons, lesson_db_cursor)
                        lesson_results = lesson_results[:lesson_page_size]

                    if exported_course.uploaded_file is not None:
                        exported_course.uploaded_file.delete()
                    exported_course.delete()
                    deleted_courses = deleted_courses + 1
    
                course_results = set_cursor(all_exported_courses, course_db_cursor)
                course_results = course_results[:course_page_size]
    
            normalized_log = unicodedata.normalize('NFKD', 'Total size: %s\n ' % (filesizeformat(total_size))).encode('ascii','ignore')
            my_file.write(normalized_log)
            
        except Exception as e:
            logging.error(traceback.format_exc())
            mail_admins('Delete old courses - exception occurred ', traceback.format_exc())
            return HttpResponse('failure')

    mail_admins('Deleted old exported courses','Old exported courses have been deleted. Full raport is available in GCS bucket under:\nhttps://console.developers.google.com/project/lorepocorporate/storage/browser%s \nTotal deleted courses: %s \nTotal deleted lessons: %s \nTotal space recovered: %s' % (log_file_name, deleted_courses, deleted_lessons, filesizeformat(total_size)))
    return HttpResponse('ok')


# cron for locking companies
def get_companies():
    companies = Space.objects.filter(space_type=SpaceType.CORPORATE, parent=None, is_deleted=False).order_by('title')

    for space in companies:
        if LockedSpaceAccess.objects.filter(space = space).count() > 0:
            space.is_blocked = True
        else:
            space.is_blocked = False
        space.users = CompanyUser.objects.filter(company = space)
        space.users_count = space.users.count()
        space.properties = get_company_properties(space)
        if space.properties.max_accounts and space.users_count > space.properties.max_accounts:
            space.user_limit_exceeded = True

    return companies


def get_owners_emails (company_users, company):
    emails = []
    for company_user in company_users:
        user = User.objects.get(username = company_user.user)
        if is_space_owner(company, user):
            emails.append(user.email)
    return emails


def get_users_emails (company_users):
    emails = []
    for company_user in company_users:
        user = User.objects.get(username = company_user.user)
        emails.append(user.email)
    return emails


@cron_method
def lock_companies_cron(_):
    logging.info('[lock_companies] lock_companies_cron start')
    _lock_companies()
    logging.info('[lock_companies] lock_companies_cron end')
    return HttpResponse('ok')


@login_required
@user_passes_test(lambda user: user.is_superuser, '/', '')
def lock_companies(request):
    _lock_companies()
    return HttpResponse('ok')


def _lock_companies():
    url = '/cron/lock_companies_async'
    trigger_backend_task(url)


def check_days_difference(first_date, second_date):
    d1 = date(first_date.year, first_date.month, first_date.day)
    d2 = date(second_date.year, second_date.month, second_date.day)
    delta = d1 - d2
    return delta.days


def get_superusers_emails():
    emails = []
    users = User.objects.filter(is_superuser=True)
    for user in users:
        emails.append(user.email)
    return emails


@backend
def lock_companies_async(request):
    try:
        companies = get_companies()
        for space in companies:
            if space.properties.valid_until is not None and (space.properties.valid_until < datetime.datetime.now() and not space.is_blocked) and space.users_count != 0:
                space_users_emails = get_users_emails(space.users)
                lock(space.id)

                space_users_subject = 'The mAuthor company space - {} has been locked.'.format(space)
                space_users_message = render_to_string('emails/space_locked.txt')

                superusers_subject = 'Space has been locked'
                superusers_message = 'Space {} has been locked'.format(space)

                superusers_emails = get_superusers_emails()

                send_message(SERVER_EMAIL, superusers_emails, superusers_subject, superusers_message)
                send_message(SERVER_EMAIL, space_users_emails, space_users_subject, space_users_message)
            elif space.properties.valid_until is not None and (check_days_difference(space.properties.valid_until, datetime.datetime.now()) == 10) and space.is_test:
                emails = get_users_emails(space.users)
                message = render_to_string('emails/middle_of_free_trial.txt')
                subject = 'Space {} access lock'.format(space)

                send_message(SERVER_EMAIL, emails, subject, message)
    except Exception:
        logging.error(traceback.format_exc())
        mail_admins('Lock companies - exception occurred ', traceback.format_exc())
        return HttpResponse('failure')

    return HttpResponse('ok')


def lock(space_id):
    company_spaces = list(get_spaces_tree(space_id))
    space_accesses = []
    for cs in company_spaces:
        space_accesses.extend(SpaceAccess.objects.filter(space=cs))
    for space_access in space_accesses:
        lsa = space_access.lock()
        lsa.save()
        space_access.delete()
    if len(space_accesses):
        company_structure_changed.send(None, company_id=space_id, user_id=None)

    return HttpResponse('ok')


@cron_method
def is_more_users_in_company_cron(_):
    logging.info('[is_more_users_in_company] is_more_users_in_company_cron start')
    _is_more_users_in_company()
    logging.info('[is_more_users_in_company] is_more_users_in_company_cron end')
    return HttpResponse('ok')


@login_required
@user_passes_test(lambda user: user.is_superuser, '/', '')
def is_more_users_in_company(request):
    _is_more_users_in_company()
    return HttpResponse('ok')


def _is_more_users_in_company():
    url = '/cron/is_more_users_in_company_async'
    trigger_backend_task(url)


@backend
def is_more_users_in_company_async(request):
    try:
        companies = get_companies()
        for company in companies:
            company_properties = get_company_properties(company)
            if company_properties.is_more_users_than_allowed():
                emails = get_owners_emails(company.users, company)

                message = render_to_string('emails/too_many_users.txt',
                                           {'company': company,
                                            'maxAccount': company.properties.max_accounts
                                            })

                subject = 'Too many users in space'
                send_message(SERVER_EMAIL, emails, subject, message)
    except Exception:
        logging.error(traceback.format_exc())
        mail_admins('Check users in company - exception occurred ', traceback.format_exc())
        return HttpResponse('failure')

    return HttpResponse('ok')