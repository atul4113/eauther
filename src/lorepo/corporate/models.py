from djangae.fields import ListField
from django.db import models
from lorepo.filestorage.models import UploadedFile
from lorepo.permission.models import Permission
from lorepo.spaces.models import Space
from django.contrib.auth.models import User
import settings

PROJECT_ADMIN_PERMISSIONS = [Permission.SPACE_ACCESS_MANAGE,
                           Permission.SPACE_EDIT,
                           Permission.SPACE_REMOVE,
                           Permission.BULK_ASSETS_UPDATE,
                           Permission.BULK_TEMPLATE_UPDATE]

class CorporateLogo(models.Model):
    logo = models.ForeignKey(UploadedFile, on_delete=models.DO_NOTHING)
    space = models.ForeignKey(Space, on_delete=models.DO_NOTHING)

class CorporatePublicSpace(models.Model):
    company = models.ForeignKey(Space, related_name="public_space_categories", on_delete=models.DO_NOTHING)
    public_category = models.ForeignKey(Space, related_name="assigned_company", on_delete=models.DO_NOTHING)

    def __str__(self):
        return '%(company)s:%(public)s' % {'company' : self.company.title, 'public' : self.public_category.title}

class CompanyProperties(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    company = models.ForeignKey(Space, on_delete=models.DO_NOTHING)
    valid_until = models.DateTimeField(null=True)
    max_accounts = models.IntegerField(null=True)
    language_code = models.CharField(max_length=20, null=True, default=settings.LANGUAGE_CODE)
    callback_url = models.CharField(max_length=300, null=True)

    def can_add_more_users(self):
        users = CompanyUser.objects.filter(company=self.company).count()
        return self.max_accounts is not None and users < self.max_accounts

    def is_more_users_than_allowed(self):
        users = CompanyUser.objects.filter(company=self.company).count()
        return self.max_accounts is not None and users > self.max_accounts


class CompanyUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    company = models.ForeignKey(Space, on_delete=models.DO_NOTHING)

    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    username = models.CharField(max_length = 200) # for better performance at sorting

    def __str__(self):
        return '%(company_name)s:%(username)s' % { 'company_name' : self.company.title, 'username' : self.username }

# !!! dont use this, use CompanyUser instead !!!
class ProjectUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    project = models.ForeignKey(Space, on_delete=models.DO_NOTHING)

    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    username = models.CharField(max_length = 200) # for better performance at sorting
    space_access_list = ListField(models.IntegerField()) # list of space access ids

    def __str__(self):
        return '%(project_name)s:%(username)s' % { 'project_name' : self.project.title, 'username' : self.username }


class JOB_TYPE(object):
    RETRIEVE = 0
    ARCHIVE = 1
    DELETE = 2


class SpaceJob(models.Model):

    STATUS_NOT_STARTED = 0
    STATUS_IN_PROGRESS = 1
    STATUS_DONE = 2
    STATUS_FAILED = 3

    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    space = models.ForeignKey(Space, on_delete=models.DO_NOTHING)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    status = models.IntegerField(default=STATUS_NOT_STARTED)
    traceback = models.TextField(blank=True)
    job_type = models.IntegerField()

    def set_status_failed(self):
        self.status = SpaceJob.STATUS_FAILED

    def set_status_done(self):
        self.status = SpaceJob.STATUS_DONE

    def set_status_in_progress(self):
        self.status = SpaceJob.STATUS_IN_PROGRESS

    def is_not_started(self):
        return self.status == SpaceJob.STATUS_NOT_STARTED

    def is_in_progress(self):
        return self.status == SpaceJob.STATUS_IN_PROGRESS

    @classmethod
    def get_instance(cls, space_id):
        return cls.objects.filter(space=space_id)

    @classmethod
    def is_any_job_in_progress(cls, space_id):
        jobs = cls.objects.filter(space=space_id, status__in=[SpaceJob.STATUS_IN_PROGRESS, SpaceJob.STATUS_NOT_STARTED]).count()
        return jobs > 0


class DemoAccountLessons(models.Model):
    my_content_demo_lesson = models.IntegerField(default=5161195309891584)

    publication_lesson_first = models.IntegerField(default=5910648580997120)
    publication_lesson_second = models.IntegerField(default=6360676558700544)
    publication_lesson_third = models.IntegerField(default=6386555325251584)

    template_lesson_first = models.IntegerField(default=5910648580997120)
    template_lesson_second = models.IntegerField(default=6360676558700544)
    template_lesson_third = models.IntegerField(default=6386555325251584)

    def set_my_content_demo_lesson(self, url):
        self.my_content_demo_lesson = url

    def set_publication_lesson_first(self, url):
        self.publication_lesson_first = url

    def set_publication_lesson_second(self, url):
        self.publication_lesson_second = url

    def set_publication_lesson_third(self, url):
        self.publication_lesson_third = url

    def set_template_lesson_first(self, url):
        self.template_lesson_first = url

    def set_template_lesson_second(self, url):
        self.template_lesson_second = url

    def set_template_lesson_third(self, url):
        self.template_lesson_third = url
