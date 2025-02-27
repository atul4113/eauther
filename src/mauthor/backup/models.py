from django.db import models
from src.lorepo.filestorage.models import UploadedFile
from src.lorepo.mycontent.models import Content

class ProjectBackup(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    backup = models.ForeignKey(UploadedFile, null=True, on_delete=models.DO_NOTHING)
    number_of_contents = models.IntegerField(default=0)

class ExportedPackage(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    zipped_content = models.ForeignKey(UploadedFile, on_delete=models.DO_NOTHING)
    project_backup = models.ForeignKey(ProjectBackup, on_delete=models.DO_NOTHING)
    content = models.ForeignKey(Content, on_delete=models.DO_NOTHING)