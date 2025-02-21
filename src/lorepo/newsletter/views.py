import datetime

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.core.mail import mail_admins
from django.shortcuts import render
from django.template import loader
from django.template.context import Context

import settings
from libraries.utility.decorators import backend
from libraries.utility.environment import is_development_server
from libraries.utility.helpers import get_object_or_none
from lorepo.filestorage.models import SecureFile
from lorepo.newsletter.models import NewsletterEmails
from django.http import HttpResponse

from lorepo.newsletter.utils import CsvFileBufferPresenter
from lorepo.public.util import send_message
from mauthor.utility.db_safe_iterator import safe_iterate

PAGE_SIZE_ITERATE = 100


def _get_data_query(newsletter_email):
    if not newsletter_email.is_all:
        date_to_find = datetime.datetime.fromtimestamp(newsletter_email.timestamp_to_run).strftime('%Y-%m-%d %H:%M:%S')
        users = User.objects.filter(date_joined__gte=date_to_find).order_by('date_joined')
    else:
        users = User.objects.all().order_by('date_joined')

    return users


def _process_batch_data_to_log(batch):
    import logging
    logging.info('[get_emails_async] logging user emails')
    secure_file = None
    counter = 0
    for batch in safe_iterate(batch, PAGE_SIZE_ITERATE):
        email_counter_batch = len(batch)
        if email_counter_batch > 0:
            logging.info('[get_emails_async] logging user emails: %s' % email_counter_batch)
            counter += email_counter_batch

    return counter, secure_file


@backend
def get_emails_async(request, newsletter_email_id):
    import logging
    user = request.user
    try:
        newsletter_email = get_object_or_none(NewsletterEmails, pk=newsletter_email_id)
        if newsletter_email is None:
            return HttpResponse('get_emails_async  returns None newsletter_email_id: %s ' % newsletter_email_id)

        newsletter_email.status = NewsletterEmails.NewsletterEmailsStatus.IN_PROGRESS
        newsletter_email.save()
        user = newsletter_email.user

        users = _get_data_query(newsletter_email)

        if is_development_server(): #on local server /_ah/gcs returns 500
            counter, secure_file = _process_batch_data_to_log(users)
        else:
            file_name = 'users_emails_%s.csv' % newsletter_email.timestamp_to_run
            content_type = 'text/csv'
            counter, secure_file = SecureFile.save_batch_data_in_gcs(
                data=users,
                file_name=file_name,
                user=user,
                content_type=content_type,
                class_presenter=CsvFileBufferPresenter
            )

        newsletter_email.emails_counter = counter
        newsletter_email.status = NewsletterEmails.NewsletterEmailsStatus.FINISHED
        newsletter_email.email_file = secure_file
        newsletter_email.save()
        send_newsletter_emails_confirmation(user, newsletter_email)
    except Exception as e:

        import traceback
        logging.error(traceback.format_exc())

        subject = '[Newsletter] get_emails_async Export users emails error: ' + str(e)
        body = traceback.format_exc()

        mail_admins(subject, body)
        if user:
            subject = 'Problem with getting email [get_emails_async]'
            body = 'Something goes wrong. Please try again later or contact us.'
            send_message(settings.DEFAULT_FROM_EMAIL, [user.email], subject, body)

    return HttpResponse('ok')


def send_newsletter_emails_confirmation(user, newsletter_email):
    subject = 'Newsletter user emails from date: %s have been successfully exported' % newsletter_email.created_date.strftime("%Y-%m-%d %H:%M")
    context = Context({'user': user, 'newsletter_email': newsletter_email, 'settings': settings})
    email = loader.get_template('newsletter/confirmation.txt')
    rendered = email.render(context)
    send_message(settings.SERVER_EMAIL, [user.email], subject, rendered)


def send_newsletter_failure_confirmation(user, newsletter_email):
    subject = 'Newsletter user emails from date: %s have not been exported' % newsletter_email
    context = Context({'user': user, 'newsletter_email': newsletter_email, 'settings': settings})
    template = loader.get_template('newsletter/failure.txt')
    email = loader.get_template(template)
    rendered = email.render(context)
    send_message(settings.SERVER_EMAIL, [user.email], subject, rendered)


@login_required
@user_passes_test(lambda user: user.is_superuser)
def index(request):
    return render(request, 'newsletter/index.html')