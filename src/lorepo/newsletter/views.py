import datetime
import logging
import os
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.core.mail import mail_admins
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.conf import settings
from django.core.files.storage import default_storage

from src.libraries.utility.decorators import backend
from src.libraries.utility.environment import is_development_server
from src.lorepo.newsletter.models import NewsletterEmails
from src.lorepo.public.util import send_message
from src.mauthor.utility.db_safe_iterator import safe_iterate

PAGE_SIZE_ITERATE = 100


def _get_data_query(newsletter_email):
    """
    Get the user query based on the newsletter email configuration.
    """
    if not newsletter_email.is_all:
        date_to_find = datetime.datetime.fromtimestamp(newsletter_email.timestamp_to_run).strftime('%Y-%m-%d %H:%M:%S')
        users = User.objects.filter(date_joined__gte=date_to_find).order_by('date_joined')
    else:
        users = User.objects.all().order_by('date_joined')
    return users


def _process_batch_data_to_log(batch):
    """
    Process batch data and log the number of users.
    """
    counter = 0
    for batch in safe_iterate(batch, PAGE_SIZE_ITERATE):
        email_counter_batch = len(batch)
        if email_counter_batch > 0:
            logging.info(f'[get_emails_async] logging user emails: {email_counter_batch}')
            counter += email_counter_batch
    return counter


def _save_batch_data_to_file(users, file_name):
    """
    Save batch data to a file on the local file system or any configured storage backend.
    """
    file_path = os.path.join('newsletter_exports', file_name)
    with default_storage.open(file_path, 'w') as file:
        for user in users:
            file.write(f'{user.email}\n')
    return len(users), file_path


def _send_confirmation_email(user, newsletter_email, template_name, subject):
    """
    Send a confirmation email to the user.
    """
    context = {
        'user': user,
        'newsletter_email': newsletter_email,
        'settings': settings
    }
    email_body = render_to_string(f'newsletter/{template_name}', context)
    send_message(settings.SERVER_EMAIL, [user.email], subject, email_body)


@backend
def get_emails_async(request, newsletter_email_id):
    """
    Asynchronously export user emails to a CSV file and send a confirmation email.
    """
    user = request.user
    try:
        newsletter_email = get_object_or_404(NewsletterEmails, pk=newsletter_email_id)
        newsletter_email.status = NewsletterEmails.NewsletterEmailsStatus.IN_PROGRESS
        newsletter_email.save()

        users = _get_data_query(newsletter_email)

        if is_development_server():
            # On local server, log the data instead of saving to a file
            counter = _process_batch_data_to_log(users)
            file_path = None
        else:
            # Save the data to a file in production
            file_name = f'users_emails_{newsletter_email.timestamp_to_run}.csv'
            counter, file_path = _save_batch_data_to_file(users, file_name)

        # Update the newsletter email status and save the file path
        newsletter_email.emails_counter = counter
        newsletter_email.status = NewsletterEmails.NewsletterEmailsStatus.FINISHED
        newsletter_email.email_file_path = file_path  # Store the file path in the model
        newsletter_email.save()

        # Send a confirmation email
        subject = f'Newsletter user emails from date: {newsletter_email.created_date.strftime("%Y-%m-%d %H:%M")} have been successfully exported'
        _send_confirmation_email(user, newsletter_email, 'confirmation.txt', subject)

    except Exception as e:
        logging.error(f'Error in get_emails_async: {str(e)}', exc_info=True)

        # Notify admins and the user about the error
        subject = '[Newsletter] get_emails_async Export users emails error'
        body = f'Error: {str(e)}\n\nTraceback:\n{logging.traceback.format_exc()}'
        mail_admins(subject, body)

        if user:
            subject = 'Problem with getting email [get_emails_async]'
            body = 'Something went wrong. Please try again later or contact us.'
            send_message(settings.DEFAULT_FROM_EMAIL, [user.email], subject, body)

    return HttpResponse('ok')


@login_required
@user_passes_test(lambda user: user.is_superuser)
def index(request):
    """
    Render the newsletter index page for superusers.
    """
    return render(request, 'newsletter/index.html')