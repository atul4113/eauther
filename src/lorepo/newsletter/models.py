from django.contrib.auth.models import User
from django.db import models

class SecureFile(models.Model):
    # Your model fields here
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='uploads/')
class NewsletterEmails(models.Model):
    class NewsletterEmailsStatus():
        DEFAULT = 0
        IN_PROGRESS = 1
        FINISHED = 2

    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    email_file = models.ForeignKey('newsletter.SecureFile', related_name='emails', on_delete=models.CASCADE)
    timestamp = models.IntegerField()
    timestamp_to_run = models.IntegerField()
    description = models.TextField()
    status = models.IntegerField(default=NewsletterEmailsStatus.DEFAULT)
    is_all = models.BooleanField(default=False)
    emails_counter = models.IntegerField(default=0)
