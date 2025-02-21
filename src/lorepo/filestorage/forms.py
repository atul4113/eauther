from django import forms
from lorepo.filestorage.models import UploadedFile

class UploadForm(forms.ModelForm):
    class Meta:
        model = UploadedFile
        exclude = ('owner', 'content_type', 'filename', 'title', 'path', 'meta', 'created_date', 'size')