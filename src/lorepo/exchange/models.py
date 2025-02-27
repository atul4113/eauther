from collections import namedtuple

from djangae.fields import ListField
from django.contrib.auth.models import User
from django.db import models

from src.lorepo.filestorage.models import UploadedFile
from src.lorepo.mycontent.models import Content


class ExportedContent(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    content = models.ForeignKey(Content, on_delete=models.DO_NOTHING)
    export = models.ForeignKey(UploadedFile, on_delete=models.DO_NOTHING)
    version = models.IntegerField(default=2)


ExportType = namedtuple("export_type", "type name")


class ExportVersions(object):
    SCORM_1_2 = ExportType(1, 'SCORM 1.2')
    SCORM_2004 = ExportType(2, 'SCORM 2004')
    SCORM_XAPI = ExportType(3, 'xAPI')
    WOMI = ExportType(4, 'WOMI')  # export type
    WOMI_HIDE_NAV = ExportType(5, 'WOMI HIDE NAV')  # export type
    HTML_5 = ExportType(6, 'HTML5')  # export type

    @classmethod
    def get_nametag(cls, export_version):
        is_export, export = cls.check_and_get_type(export_version)
        if is_export:
            return export.name

    @classmethod
    def check_and_get_type(cls, version):
        export_versions = cls.get_exported_versions()
        for export_version in export_versions:
            if version is not None and (int(version) == export_version.type):
                return True, export_version

        return False, None

    @classmethod
    def get_exported_versions(cls):
        attributes = (getattr(cls, attribute) for attribute in vars(cls))
        versions_attributes = (attribute for attribute in attributes if isinstance(attribute, tuple))
        return list(versions_attributes)


class ExportFails(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    content_id = models.IntegerField()
    session_id = models.CharField(max_length=100)


class ExportWOMIPages(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    in_progress = models.BooleanField(default=False)
    is_success = models.BooleanField(default=False)
    content = models.ForeignKey(Content, on_delete=models.DO_NOTHING)
    hide_nav = models.BooleanField(default=False)
    commons_indexes = ListField(models.IntegerField())
    pages_count = models.IntegerField(default=-1)
    traceback = models.TextField(blank=True, null=True)

    @property
    def version(self):
        return ExportVersions.WOMI_HIDE_NAV.type if self.hide_nav else ExportVersions.WOMI.type

    @property
    def packages(self):
        return [export.exported_womi_package for export in ExportWOMIPage.objects.filter(pages_export=self)]

    @property
    def sorted_packages(self):
        pages_exports = ExportWOMIPage.objects.filter(pages_export=self)
        pages_exports = sorted(pages_exports, key=lambda page: page.page_index)
        return [export.exported_womi_package for export in pages_exports]


class ExportWOMIPage(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    pages_export = models.ForeignKey(ExportWOMIPages, on_delete=models.DO_NOTHING)
    in_progress = models.BooleanField(default=False)
    is_finished = models.BooleanField(default=False)
    is_success = models.BooleanField(default=False)
    page_index = models.IntegerField()
    page_content = models.ForeignKey(UploadedFile, null=True, on_delete=models.DO_NOTHING, related_name="+")
    exported_womi_package = models.ForeignKey(UploadedFile, null=True, on_delete=models.DO_NOTHING, related_name="+")
    traceback = models.TextField(blank=True, null=True)

    @property
    def content(self):
        return self.pages_export.content
