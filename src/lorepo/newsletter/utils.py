import csv
import time
import io

from django.contrib.auth.models import User

from src.libraries.utility.environment import get_versioned_module
from src.libraries.utility.helpers import get_object_or_none
from src.libraries.utility.queues import trigger_backend_task
from src.lorepo.corporate.models import CompanyUser
from src.lorepo.newsletter.models import NewsletterEmails
import src.libraries.utility.cacheproxy as cache
from src.lorepo.spaces.models import Space


class CsvFileBufferPresenter(object):

    @staticmethod
    def get_presentation(batch, loop_counter):
        header = ['username', 'email', 'company']
        out_file = io.StringIO()

        writer = csv.writer(out_file, delimiter=",")
        if loop_counter == 0:
            writer.writerow(header)

        for user in batch:
            company_user = get_object_or_none(CompanyUser, user=user)
            try:
                company_name = company_user.company.title.encode('utf-8')
            except (AttributeError, Space.DoesNotExist, User.DoesNotExist):
                import logging
                logging.error('no space for company_user: %s ' % user.username)
                company_name = '---no-space-----'
            writer.writerow([user.username.encode('utf-8'), user.email.encode('utf-8'), company_name])

        return out_file


class NewsletterEmailProcessor(object):
    TIME_WINDOW = 120 #how many seconds wait for new account created

    @staticmethod
    def process_all_mode(request, timestamp, is_all):
        NewsletterEmailProcessor.schedule_task(request.user, timestamp, is_all)
        return {
            'message': 'Task scheduled correctly. Please wait for an email.',
            'code': 1
        }

    @staticmethod
    def process_all_count_not_cached(request, timestamp):
        is_all = False

        newsletter_emails_all_count = NewsletterEmails.objects.filter(status=NewsletterEmails.NewsletterEmailsStatus.FINISHED).count()
        if newsletter_emails_all_count == 0:
            is_all = True
        else:
            cache.set("newsletter_emails_all_count", newsletter_emails_all_count, 6 * 60 * 60)

        NewsletterEmailProcessor.schedule_task(request.user, timestamp, is_all)
        response = {
            'message': 'Task scheduled correctly. Please wait for an email.',
            'code': 1
        }

        return response

    @staticmethod
    def process_in_time_window(timestamp):
        response = None
        newsletter_email = NewsletterEmails.objects.filter(status=NewsletterEmails.NewsletterEmailsStatus.FINISHED, timestamp__gte=timestamp - NewsletterEmailProcessor.TIME_WINDOW).order_by('-timestamp').first()
        if newsletter_email:
            response = NewsletterEmailProcessor.process_are_new_accounts(newsletter_email)
            if response is not None:
                return response

        return response

    @staticmethod
    def process_are_new_accounts(newsletter_email):

        if newsletter_email.emails_counter > 0:
            link = newsletter_email.email_file.link if newsletter_email.email_file else ''
            return {
                'message': 'Email with data has been sent correctly on: %s. You can get file by clicking the link.' % newsletter_email.created_date.strftime(
                    '%Y-%m-%d %H:%M:%S'),
                'link': link,
                'code': 3
            }
        elif newsletter_email.emails_counter == 0:
            return {
                'message': 'There are no new accounts since: %s. ' % newsletter_email.created_date.strftime(
                    '%Y-%m-%d %H:%M:%S'),
                'code': 1
            }

    @staticmethod
    def process_get_new_newsletter_emails(request, is_all):

        newsletter_emails = NewsletterEmails.objects.filter(status=NewsletterEmails.NewsletterEmailsStatus.FINISHED).order_by('-timestamp')
        if len(newsletter_emails) == 0:
            cache.delete("newsletter_emails_all_count")
            return {'message': 'Unexpected error. Please try again later.', 'code': 1}

        timestamp = newsletter_emails[0].timestamp
        NewsletterEmailProcessor.schedule_task(request.user, timestamp, is_all)

        return {
            'message': 'Task scheduled correctly. Please wait for an email.',
            'code': 1
        }

    @staticmethod
    def schedule_task(user, timestamp, is_all):
        newsletter_email = NewsletterEmails(
            user=user,
            timestamp_to_run=timestamp,
            timestamp=int(time.time()),
            is_all=is_all
        )
        newsletter_email.save()

        trigger_backend_task('/newsletter/get_emails_async/%s' % newsletter_email.id,
                             target=get_versioned_module('download'),
                             queue_name='download')