import logging
import mimetypes
import zipfile

import src.cloudstorage as gcs
from django.db import models

from src.libraries.utility.BucketManager import BucketManager
from src.libraries.utility.environment import is_development_server
from src.lorepo.filestorage.models import UploadedFile
from src.lorepo.filestorage.utils import get_reader
from src.lorepo.translations.models import SupportedLanguages
from src.settings import get_bucket_name


class WebSite(models.Model):
    PAGE_BUCKET = get_bucket_name('imported-resources')[1:]
    FOLDER_PREFIX = 'home-page'
    ZIP_MAX_FILES = None  # maximum number of files allowed in package, int or None
    ZIP_MAX_SIZE = 15 * 1024 * 1024
    GCS_OPTIONS = {'x-goog-acl': 'public-read'}

    class Status():
        IN_PROGRESS = 'in_progress'
        SERVING = 'serving'
        EMPTY = 'empty'

    class ZipFileException(Exception):
        pass

    modified_date = models.DateTimeField(auto_now_add=True)
    uploaded_zip = models.ForeignKey(UploadedFile, null=True, on_delete=models.DO_NOTHING)
    version = models.CharField(max_length=200, null=False, choices=[('Version 1', 'v1'), ('Version 2', 'v2')])
    status = models.CharField(max_length=50, default=Status.EMPTY)
    language = models.ForeignKey(SupportedLanguages, null=True, on_delete=models.CASCADE)

    @property
    def bucket_manager(self):
        try:
            return self._bucket_manager
        except AttributeError:
            self._bucket_manager = BucketManager(self.PAGE_BUCKET, self.FOLDER_PREFIX)
            return self._bucket_manager

    @property
    def temp_folder(self):
        return self.bucket_manager.bucket_name + '/temp/'

    @property
    def url(self):
        if self.status == WebSite.Status.SERVING:
            if is_development_server():
                prefix = '/_ah/gcs'
            else:
                prefix = 'https://storage.googleapis.com'
            return prefix + self.bucket_manager.get_bucket_file_name(
                '{}_{}'.format(self.language.lang_key, self.version)) + '/index.html'
        else:
            return None

    def __validate_zipfile(self, namelist):
        if WebSite.ZIP_MAX_FILES and len(namelist) > WebSite.ZIP_MAX_FILES:
            raise WebSite.ZipFileException('plain.admin.panel.home_websites.file_not_valid.max_files')
        if 'index.html' not in namelist:
            raise WebSite.ZipFileException('plain.admin.panel.home_websites.file_not_valid.no_index_html')

    def validate_zipfile(self, up):
        blob_reader = get_reader(up)
        with zipfile.ZipFile(blob_reader) as zf:
            namelist = zf.namelist()
            self.__validate_zipfile(namelist)

    def extract(self):
        mimetypes.init()
        mimetypes.add_type('image/svg+xml', '.svg')
        blob_reader = get_reader(self.uploaded_zip)
        bm = BucketManager(self.PAGE_BUCKET, "%s/%s_%s" % (self.FOLDER_PREFIX, self.language.lang_key, self.version))
        with zipfile.ZipFile(blob_reader) as zf:
            namelist = zf.namelist()
            self.__validate_zipfile(namelist)
            logging.info(namelist)
            for name in namelist:
                if name[-1] != '/':  # not a 'dir'
                    with zf.open(name) as oldf:
                        new_path = bm.get_bucket_file_name(name)
                        with gcs.open(new_path, 'w', content_type=mimetypes.guess_type(name)[0],
                                      options=self.GCS_OPTIONS) as newf:
                            newf.write(oldf.read())
        self.uploaded_zip.file.file.blobstore_info.delete()
        self.uploaded_zip = None
        self.status = WebSite.Status.SERVING
        self.save()

    def cleanup(self):
        self.bucket_manager.delete_with_prefix(self.version)
