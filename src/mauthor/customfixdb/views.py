from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import HttpResponse
from libraries.utility.cursors import set_cursor, get_cursor
from libraries.utility.decorators import backend
from libraries.utility.helpers import get_object_or_none
from libraries.utility.queues import trigger_backend_task
from libraries.utility.environment import get_versioned_module, get_app_version
from django.contrib.auth.decorators import login_required, user_passes_test
from lorepo.public.util import send_message
from mauthor.customfixdb.models import FixLog
from mauthor.customfixdb.util import object_builder
import settings

FIXDB_QUEUE = 'search'
FIXDB_MODULE = 'backup'


@backend
def generic_async(request, user_id, page_size, instance_name, cursor=None, task_number = 0):
    user = get_object_or_none(User, pk=user_id)
    retry_count = 1
    try:
        page_size = int(page_size)
        task_number = int(task_number)
        backend_task_config_instance = object_builder(instance_name)
        queryset = backend_task_config_instance.get_queryset()
        if cursor is None:
            results = queryset[0:page_size]
        else:
            queryset = set_cursor(queryset, cursor)
            results = queryset[0:page_size]
        if len(results) == page_size:
            #this is not the last task = make another
            cursor = get_cursor(results)
            url = '/customfixdb/generic_async/%s/%d/%s/%s/%d' % (user_id, page_size, instance_name, cursor, task_number+1)
            trigger_backend_task(url, target=get_versioned_module(FIXDB_MODULE), queue_name=FIXDB_QUEUE)
        else:
            #this is the last task = send summary
            subject = '[customfixdbconfig] Version: %s  customfixdbconfig: [%s] - created tasks in total: %d ' % (get_app_version(), instance_name, task_number+1)
            body = 'Version: %s ' % (get_app_version())
            backend_task_config_instance.send_success(user, instance_name, subject, body)

        #do the actual work, should not be subjected to retries
        try:
            backend_task_config_instance.logic(results)
            subject = '[customfixdbconfig] Version: %s customfixdbconfig: [%s] Task number: %d finished correctly' % (get_app_version(),instance_name, task_number)
            body = 'Version: %s  task number %s on customfixdbconfig %s ' % (get_app_version(), task_number, instance_name)
            backend_task_config_instance.send_success(user, instance_name, subject, body, task_number = task_number)
        except Exception:
            import traceback
            backend_task_config_instance.send_failure(user, task_number, retry_count, instance_name, traceback, cursor)

    except Exception:
        import traceback
        subject = '[customfixdbconfig] Error in configuration version: %s  customfixdbconfig: [%s]' % (get_app_version(), instance_name)
        send_message(settings.SERVER_EMAIL, [user.email] , subject, traceback.format_exc())
        return HttpResponse('failure')

    return HttpResponse('ok')


@login_required
@user_passes_test(lambda user: user.is_superuser, '/', '')
def manage(request):
    page_size = config_instance_name = ''
    wrong_config_instance_name = ''
    wrong_page_size = ''

    if request.method == 'POST':
        page_size = request.POST.get('page_size')
        config_instance_name = request.POST.get('config_instance_name')

        try:
            page_size = int(page_size)
        except ValueError:
            wrong_page_size = "Page size must be numeric"

        if len(config_instance_name) == 0:
            wrong_config_instance_name = 'You have to add config instance name'
        try:
            object_builder(config_instance_name)
            url = '/customfixdb/generic_async/%s/%s/%s' % (request.user.id, page_size, config_instance_name)
            trigger_backend_task(url, target=get_versioned_module(FIXDB_MODULE), queue_name=FIXDB_QUEUE)
            messages.success(request, 'You should receive emails with results')
        except:
            wrong_config_instance_name = 'You have to add existing config instance name'

    return render(request, 'admin/manage_customfixdb.html', {
        'config_instance_name': config_instance_name,
        'page_size': page_size,
        'wrong_page_size': wrong_page_size,
        'wrong_config_instance_name': wrong_config_instance_name,
        'next_url': '/panel/dev'
    })


@login_required
@user_passes_test(lambda user: user.is_superuser, '/', '')
def report(request, slug):
    logs = FixLog.objects.filter(slug=slug).order_by('-modified_date')
    if slug.startswith('test_ssl_'):  #temp
        slug = 'ssl'
    return render(request, 'admin/fixdb_report.html', {
        'logs': logs,
        'data_template': 'admin/reports/{0}.html'.format(slug)
    })
