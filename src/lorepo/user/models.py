from django.contrib.auth.models import User
from django.db import models

from lorepo.translations.models import SupportedLanguages
from settings import LANGUAGE_CODE

# depreciated
class UserLanguage(models.Model):
    created_date = models.DateTimeField(auto_now_add = True)
    modified_date = models.DateTimeField(auto_now = True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    language_code = models.CharField(max_length=20, null=True, default=LANGUAGE_CODE)


class UserProfile(models.Model):
    created_date = models.DateTimeField(auto_now_add = True)
    modified_date = models.DateTimeField(auto_now = True)
    user = models.OneToOneField(User, related_name="profile", on_delete=models.DO_NOTHING)
    language_code = models.CharField(max_length=20, null=True, default=LANGUAGE_CODE)
    favourite_modules = models.TextField(null=True, default="")
    render_view = models.BooleanField(default=True)
    lang = models.ForeignKey(SupportedLanguages, null=True, on_delete=models.DO_NOTHING)
