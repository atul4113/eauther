from lorepo.filestorage.models import UploadedFile
from lorepo.public.util import send_message
from libraries.utility.decorators import service_admin_user
from django.template import loader
from django.template.context import Context
from django.contrib.auth.models import User
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from libraries.utility.environment import get_versioned_module
from libraries.utility.queues import trigger_backend_task
import json
import logging
from settings import get_bucket_name


@service_admin_user
def gce_callback(request, space_id, user_id, file_name):
    user = User.objects.get(pk=user_id)
    uploaded_file = UploadedFile(path="%s/gce_exchange/import_pdf/%s/%s/%s" % (get_bucket_name('imported-resources'), space_id, user_id, file_name), filename=file_name, owner=user)
    uploaded_file.save()
    url = "/exchange/import/%(file_id)s/%(user_id)s" % {'file_id': uploaded_file.id, 'user_id': user_id}
    if space_id:
        url = url + '/' + space_id
    trigger_backend_task(url, target=get_versioned_module('download'), queue_name='download')
    return HttpResponse('OK')

@service_admin_user
def error_message_exception(request):
    if request.method == 'POST':
        request_data = json.loads(request.raw_post_data)
        logging.error("PDF import failer")
        logging.error(request_data['traceback'])
        user = get_object_or_404(User, pk=request_data['user_id'])
        send_import_failure_notification(user, request_data['pdf_name'])
        return HttpResponse("OK")


def send_import_failure_notification(user, content = None, path='pdfimport/import_failure.txt'):
    subject = 'PDF %s has not been successfully imported' % (content or '')
    context = Context({ 'content' : content or '', 'user' : user, 'app_name' : settings.APP_NAME })
    email = loader.get_template(path)
    rendered = email.render(context)

    send_message(settings.SERVER_EMAIL, [user.email], subject, rendered)

