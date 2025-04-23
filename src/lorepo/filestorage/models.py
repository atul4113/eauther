import json
import uuid
import random
import logging
import time
import datetime
import io
from django.db import models
from django.contrib.auth.models import User
from google.cloud import storage
from src.libraries.utility.BucketManager import FileStorageBucketManager
from src.libraries.utility.environment import get_versioned_module
from src.libraries.utility.helpers import get_object_or_none, generate_unique_gcs_path
from src.libraries.utility.queues import trigger_backend_task
from src.settings import get_bucket_name

DEFAULT_HEIGHT_FACEBOOK = 200
DEFAULT_WIDTH_FACEBOOK = 200
IMAGE_HEADER_SIZE = 50000
UNSET_FILE_SIZE = -1
MAX_RETRIES = 10


class FileStorage(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    content_type = models.CharField(max_length=200)
    contents = models.BinaryField()
    owner = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    version = models.IntegerField(blank=True, null=True)
    history_for = models.ForeignKey('mycontent.Content', blank=True, null=True, on_delete=models.DO_NOTHING)
    meta = models.TextField(null=True)

    _gcs_contents_filename = models.CharField(max_length=1024, null=True)
    __is_saving = False
    DATASTORE_MAXIMUM_SIZE = 900000

    def __init__(self, *args, **kwargs):
        self.while_initializing = True
        self.__old_gcs_contents_filename = None
        self._gcs_contents_filename = None
        super().__init__(*args, **kwargs)
        self.while_initializing = False

    def __getattribute__(self, item):
        if item == 'contents':
            if not hasattr(self, '_gcs_contents_filename'):
                return None
            try:
                return self._get_contents()
            except self.DoesNotExist:
                return None
        return super().__getattribute__(item)

    def __setattr__(self, key, value):
        if key == 'contents':
            if hasattr(self, '_gcs_contents_filename'):
                self.__old_gcs_contents_filename = self._gcs_contents_filename
                self._gcs_contents_filename = None
        super().__setattr__(key, value)

    def _get_contents(self):
        if self._gcs_contents_filename is None:
            return super().__getattribute__('contents')
        return self._get_contents_from_gcs()

    def _save_contents(self):
        if len(self.contents) > self.DATASTORE_MAXIMUM_SIZE:
            self._save_contents_to_gcs(self.contents)

    def _save_contents_to_gcs(self, value):
        file_name = generate_unique_gcs_path(bucket='saved_content', name='content')
        bucket_manager = FileStorageBucketManager()
        bucket_manager.save(file_name, value)
        self._gcs_contents_filename = file_name
        super().__setattr__('contents', b'')

    def _get_contents_from_gcs(self):
        if self.__is_saving:
            return b''
        bucket_manager = FileStorageBucketManager()
        return bucket_manager.get(self._gcs_contents_filename)

    def _remove_old_from_gcs(self):
        if self.__old_gcs_contents_filename:
            trigger_backend_task(
                '/file/remove_old_gcs_async',
                target=get_versioned_module('localization'),
                countdown=datetime.timedelta(hours=1).total_seconds(),
                payload=json.dumps({'path': self.__old_gcs_contents_filename})
            )

    def save(self, *args, **kwargs):
        self.__is_saving = True
        try:
            # Save contents to GCS if needed before saving to Datastore
            self._save_contents()
            entity = super().save(*args, **kwargs)
            return entity
        except Exception as e:
            logging.exception(e)
            raise
        finally:
            self.__is_saving = False
            self._remove_old_from_gcs()

    def getCopy(self, author, contents=None):
        """Creates a copy of this file storage with a new author."""
        new_file = FileStorage(
            content_type=self.content_type,
            owner=author,
            version=self.version,
            history_for=self.history_for,
            meta=self.meta
        )
        
        if contents is not None:
            new_file.contents = contents
        else:
            new_file.contents = self.contents
            
        return new_file


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

    def save(self, *args, **kwargs):
        if not self.file and self.path:
            self.file = str(self.path)
        if self.size == UNSET_FILE_SIZE or self.size is None:
            self.update_size()
        return super().save(*args, **kwargs)

    def update_size(self):
        if self.path:
            retries_count = 0
            client = storage.Client()
            while retries_count < MAX_RETRIES:
                retries_count += 1
                try:
                    blob = client.bucket(get_bucket_name()).get_blob(self.path)
                    if blob:
                        self.size = blob.size
                        return
                except Exception:
                    logging.error(f'Retry {retries_count} for uploaded_file={self.id}')
                    time.sleep(random.randint(0, 4))
            raise TimeoutError(f'Max retries exceeded for uploaded_file={self.id}')

    class Meta:
        abstract = True


class UploadedFile(BaseUploadedFile):
    @property
    def link(self):
        return f'{settings.BASE_URL}/file/serve/{self.id}'
