import json
import uuid

from djangae.fields import ListField
import random
import logging
import time
from google.appengine.api import images
from google.appengine.ext import blobstore
import cloudstorage as gcs
import settings
from cloudstorage.errors import NotFoundError
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
import datetime
import io
from libraries.utility.BucketManager import FileStorageBucketManager
from libraries.utility.environment import get_versioned_module
from libraries.utility.helpers import get_object_or_none, generate_unique_gcs_path
from libraries.utility.queues import trigger_backend_task
from mauthor.utility.db_safe_iterator import safe_iterate
from settings import get_bucket_name
from google.appengine.runtime.apiproxy_errors import DeadlineExceededError

DEFAULT_HEIGHT_FACEBOOK = 200
DEFAULT_WIDTH_FACEBOOK = 200
IMAGE_HEADER_SIZE = 50000
UNSET_FILE_SIZE = -1
MAX_RETRIES = 10


class FileStorage(models.Model):
    """
    If content size is above than DATASTORE_MAXIMUM_SIZE then save it to GCS.

    Warning:
    getattribute and setattr are override (for contents field):
        getattribute: if  _gcs_contents_filename is existing then return data from GCS.
        setattr: always set  _gcs_contents_filename to None

    While saving data to database, __is_saving flag is set to True, because django will try to get
    contents (for saving it to database) where getter is override and will return value from GCS if is too large.
    So if __is_saving is True then don't return data from gcs (return empty string).
    After saving always this flag should be set to False.

    After saving an entity, a backend task will be called automatically, which removes a file from gcs. This task will
    be called after 1 hour from triggering him.
    """
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    content_type = models.CharField(max_length=200)
    contents = models.BinaryField()
    owner = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    version = models.IntegerField(blank=True, null=True)
    history_for = models.ForeignKey('mycontent.Content', blank=True, null=True, on_delete=models.DO_NOTHING)
    meta = models.TextField(null=True)

    _gcs_contents_filename = models.CharField(max_length=1024, null=True)

    __is_saving = False  # If content is while saving and is too large then return empty string (was saved to gcs)

    DATASTORE_MAXIMUM_SIZE = 900000

    def __init__(self, *args, **kwargs):
        self.while_initializing = True  # While initializing object we dont want to clear gcs path while setting contents
        self.__old_gcs_contents_filename = None
        super(FileStorage, self).__init__(*args, **kwargs)

    def __getattribute__(self, item):
        if item == 'contents':
            return self._get_contents()

        return super(FileStorage, self).__getattribute__(item)

    def __setattr__(self, key, value):
        if key == 'contents':
            if hasattr(self, '_gcs_contents_filename'):
                self.__old_gcs_contents_filename = self._gcs_contents_filename

            if self.while_initializing:
                self.while_initializing = False
            else:
                self._gcs_contents_filename = None
        super(FileStorage, self).__setattr__(key, value)

    def __enter__(self):
        if self._gcs_contents_filename is not None:
            self.__file_handler = FileStorageBucketManager().get_file_handler(self._gcs_contents_filename)
            return self.__file_handler

        file_like_object = io.StringIO(self.contents)

        return file_like_object

    def __exit__(self, *args, **kwargs):
        if hasattr(self, '__file_handler'):
            self.__file_handler.close()

    def __str__(self):
        return self.content_type

    def save(self, *args, **kwargs):
        self.__is_saving = True   # while saving this entry we want empty content from getter if this content is too large

        try:
            self._save_contents()
            entity = super(FileStorage, self).save(*args, **kwargs)   # save to datastore all data
        except Exception as e:
            import traceback
            logging.exception(traceback.format_exc())
            raise e
        else:
            self._remove_old_from_gcs()
            return entity
        finally:
            self.__is_saving = False  # always disable this flag after saving

    def _get_contents(self):
        if self._gcs_contents_filename is None:
            return models.Model.__getattribute__(self, 'contents')  # get original contents value
        else:
            return self._get_contents_from_gcs()

    def _save_contents(self):
        content_size = len(self.contents)

        if content_size > self.DATASTORE_MAXIMUM_SIZE:
            self._save_contents_to_gcs(self.contents)

    def _save_contents_to_gcs(self, value):
        file_name = generate_unique_gcs_path(bucket="saved_content", name="content")

        bucket_manager = FileStorageBucketManager()
        bucket_manager.save(file_name, value)
        self._gcs_contents_filename = file_name

        super(FileStorage, self).__setattr__('contents', '')

    def _get_contents_from_gcs(self):
        if self.__is_saving:
            return ''

        bucket_manager = FileStorageBucketManager()
        return bucket_manager.get(self._gcs_contents_filename)

    def _remove_old_from_gcs(self):
        if self.__old_gcs_contents_filename is not None:
            trigger_backend_task(
                '/file/remove_old_gcs_async',
                target=get_versioned_module('localization'),
                countdown=datetime.timedelta(hours=1).total_seconds(),
                payload=json.dumps({
                    'path': self.__old_gcs_contents_filename
                }))

    def getCopy(self, author, contents=None):
        ''' Create new page file. Return created object
        '''
        now = datetime.datetime.now()
        contents = self.contents if contents is None else contents
        pageFile = FileStorage(
                           created_date = now,
                           modified_date = now,
                           content_type = self.content_type,
                           contents = contents,
                           owner = author)
        pageFile.save()

        return pageFile


class BaseUploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/%Y/%m/%d/%H/%M/%S/')
    content_type = models.CharField(max_length=200, null=True)
    owner = models.ForeignKey(User, null=True, on_delete=models.DO_NOTHING)
    filename = models.CharField(max_length=200, null=True)
    title = models.CharField(max_length=200, null=True)
    path = models.CharField(max_length=10000, null=True)
    meta = models.TextField(null=True)
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    size = models.IntegerField(default=UNSET_FILE_SIZE)

    @staticmethod
    def get_by_href(href):
        file_id = int(href.split('/')[-1])
        return get_object_or_none(UploadedFile, pk=file_id)

    def calculate_uploaded_image_meta(self):
        width = DEFAULT_WIDTH_FACEBOOK
        height = DEFAULT_HEIGHT_FACEBOOK
        #from https://groups.google.com/forum/#!topic/google-appengine-python/avUg-ADHanI
        try:
            if self.file.file.blobstore_info:
                blob_key = self.file.file.blobstore_info.key()
            else:
                blob_key = str(self.file.file)
            data = blobstore.fetch_data(blob_key, 0, IMAGE_HEADER_SIZE)
            image = images.Image(image_data=data)
            width = image.width
            height = image.height
        except Exception:
            import logging
            import traceback
            logging.error(traceback.format_exc())

        import json
        self.meta = json.dumps({"width": width, "height": height})

    def save(self, *args, **kwargs):
        if not self.file and self.path:
            self.file = str(blobstore.create_gs_key('/gs' + self.path))
        if self.size == UNSET_FILE_SIZE or self.size is None:
            self.update_size()
        return super(BaseUploadedFile, self).save(*args, **kwargs)

    def update_size(self):
        if self.file and self.file.file.blobstore_info is not None:
            self.size = self.file.file.blobstore_info.size
        elif self.path:
            retries_count = 0
            while retries_count < MAX_RETRIES:
                retries_count += 1
                logging.debug('Get from GCS %s for uploaded_file=%s' % (retries_count, self.id))
                try:
                    stat = gcs.stat(self.path)
                    self.size = stat.st_size
                    return
                except DeadlineExceededError:
                    logging.error('Retry %s for uploaded_file=%s' % (retries_count, self.id))
                    time.sleep(random.randint(0,4))
            raise DeadlineExceededError('The maximum number of attempts for uploaded_file=%s has been exceeded' % self.id)

    def get_size(self):
        if self.size == UNSET_FILE_SIZE or self.size is None:
            self.update_size()
            self.save()
        return self.size


    @classmethod
    def create_in_gcs(cls, bucket=get_bucket_name('imported-resources')[1:], path=None, file_name='test.txt',
                      content_type='text/plain'):  # get_bucket_name('imported-resources')[1:]
        now = datetime.datetime.now()
        if path is None:
            path = '/%s/_%s/%s-%s-%s/%s_%s/%s/%s' % (
                bucket, cls.__name__.lower(), now.year, now.month, now.day, now.hour, now.minute, str(uuid.uuid4()),
                file_name)
        else:
            path = '/%s/%s/%s' % (bucket, path, file_name)
        return cls(filename=file_name, content_type=content_type, path=path)

    def gcs_handler(self, mode='r'):
        if 'r' == mode:
            return gcs.open(self.path, mode)
        return gcs.open(self.path, mode, self.content_type)

    @property
    def link(self):
        raise NotImplementedError()

    class Meta:
        abstract = True


class UploadedFile(BaseUploadedFile):

    @staticmethod
    def get_by_href(href):
        file_id = int(href.split('/')[-1])
        return get_object_or_none(UploadedFile, pk=file_id)


    @property
    def link(self):
        return '%s/file/serve/%s' % (settings.BASE_URL, self.id)


class SecurityLevels(object):
    ALL_AUTHORIZED = 1
    OWNER = 2
    STAFF = 3
    SUPERUSER = 4
    OWNER_AND_RECIPIENTS = 5
    SUPERUSER_RECORDED = 6


class SecureFile(BaseUploadedFile):
    security_level = models.IntegerField(default=SecurityLevels.SUPERUSER)
    recipients = ListField(models.IntegerField)

    @property
    def link(self):
        return '%s/file/secure/%s' % (settings.MAUTHOR_BASIC_URL, self.id)

    def has_access(self, user):
        if self.security_level == SecurityLevels.SUPERUSER_RECORDED:
            if user.is_superuser:
                self.record_access(user)
                return True
            return False
        if self.security_level == SecurityLevels.SUPERUSER:
            return user.is_superuser
        if self.security_level == SecurityLevels.STAFF:
            return user.is_staff or user.is_superuser
        if self.security_level == SecurityLevels.OWNER:
            return self.owner == user
        if self.security_level == SecurityLevels.OWNER_AND_RECIPIENTS:
            return user.is_superuser or self.owner == user or user.id in self.recipients
        if self.security_level == SecurityLevels.ALL_AUTHORIZED:
            return user.is_authenticated()
        return False

    def record_access(self, user):
        SecureFileAccessRecord(
            user=user,
            secure_file=self
        ).save()

    @classmethod
    def save_batch_data_in_gcs(cls, data, file_name, user, content_type, class_presenter):
        page_size_iterate = 100
        counter = 0
        loop_counter = 0
        secure_file = SecureFile.create_in_gcs(file_name=file_name, content_type=content_type)

        with secure_file.gcs_handler('w') as created_file:
            for batch in safe_iterate(data, page_size_iterate):
                email_counter_batch = len(batch)
                if email_counter_batch > 0:
                    out_buf = class_presenter.get_presentation(batch, loop_counter)
                    created_file.write(out_buf.getvalue())
                    counter += email_counter_batch
                    out_buf.close()
                loop_counter += 1
            created_file.close()
        secure_file.owner = user
        secure_file.security_level = SecurityLevels.SUPERUSER_RECORDED
        secure_file.save()

        return counter, secure_file


class SecureFileAccessRecord(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.DO_NOTHING)
    created_date = models.DateTimeField(auto_now_add=True)
    secure_file = models.ForeignKey(SecureFile, null=True, on_delete=models.DO_NOTHING)


def base_uploaded_file_delete(sender, instance, **kwargs):
    if instance.file.file.blobstore_info is not None:
        blobstore_info = instance.file.file.blobstore_info
        return blobstore_info.delete()
    else:
        try:
            return gcs.delete(instance.path)
        except NotFoundError as e:
            return False


@receiver(pre_delete, sender=UploadedFile)
def uploaded_file_delete(sender, instance, **kwargs):
    return base_uploaded_file_delete(sender, instance, **kwargs)


@receiver(pre_delete, sender=SecureFile)
def securefile_delete(sender, instance, **kwargs):
    return base_uploaded_file_delete(sender, instance, **kwargs)