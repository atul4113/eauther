import logging
from django.utils.log import AdminEmailHandler


class LogAdminEmailHandler(AdminEmailHandler):

    def send_mail(self, subject, message, *args, **kwargs):
        logging.error("MAIL_ADMINS: "+ subject)
        logging.error(message)