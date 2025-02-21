import functools
from lorepo.filestorage.forms import UploadForm
from django.core.exceptions import ValidationError
import re

is_file_pdf_format = functools.partial(re.search, '.+\.pdf$')


class PDFUploadForm(UploadForm):
    def clean(self):
        cleaned_data = super(PDFUploadForm, self).clean()
        if cleaned_data.get('file') is not None:
            # If filename don't have .pdf
            if not is_file_pdf_format(cleaned_data.get('file').name.lower()):
                raise ValidationError('File must be of type PDF.')

        return cleaned_data