from unidecode import unidecode
import re
from django.core.exceptions import ValidationError
import string

def make_url(title):
    url = unidecode(title)
    url = url.translate(string.maketrans('', ''), '/!@#$%^&*()+')
    url = url.strip()
    url = re.sub('[ \t]+', '-', url)
    if url == '':
        raise ValidationError("Invalid title")
    return url

def has_access_to_wiki(user):
    return True if user.is_superuser or user.is_staff else False

def get_kids(parent):
    return parent.kids.all() if parent.kids.count() > 0 else []