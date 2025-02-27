import json
import re
import zlib

from django.contrib.auth.models import User
from django.db import models
from django.db.models import BinaryField
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

import src.libraries.utility.cacheproxy as cache
from src.libraries.utility.decorators import cached_in_request
from src.lorepo.filestorage.models import UploadedFile
from src.lorepo.translations.images import images_labels
from src.lorepo.util.singleton_model import SingletonModel
from rest_framework.exceptions import ValidationError
from src.settings import USER_DEFAULT_LANG

SUPPORTED_LANGUAGES_CACHE_KEY = 'supported_languages_v1'


class SupportedLanguages(models.Model):
    lang_key = models.CharField(max_length=7)
    lang_description = models.CharField(max_length=30)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return '%s (%s)' % (self.lang_description, self.lang_key)

    @property
    def icon_key(self):
        if len(self.lang_key) >= 2:
            return self.lang_key[:2].lower()
        else:
            return 'en'

    @classmethod
    def get_languages(cls):
        return SupportedLanguages.objects.all().order_by('lang_key')

    @classmethod
    def get_languages_json(cls):
        languages = cls.get_cached_languages()
        return [{'id': lang.id, 'key': lang.lang_key, 'description': lang.lang_description} for lang in languages]

    @classmethod
    def get_cached_languages(cls):
        languages = cache.get(SUPPORTED_LANGUAGES_CACHE_KEY)

        if not languages:
            languages = cls.get_languages()
            cls.set_cached_languages(languages)
        return languages

    @classmethod
    def get_cached_language(cls, lang_id=None, lang_key=None):
        languages = cls.get_cached_languages()
        language = None

        try:
            if lang_id:
                language = [lang for lang in languages if lang.id == lang_id][0]
            elif lang_key:
                language = [lang for lang in languages if lang.lang_key == lang_key][0]
        except IndexError:
            pass

        return language

    @classmethod
    def set_cached_languages(cls, languages=None, added=None, updated=None, deleted=None):
        if languages is None:
            languages = cls.get_languages()

        languages = list(languages)
        if added is not None:
            languages.append(added)
        if deleted is not None:
            languages = [lang for lang in languages if lang.id != deleted.id]
        if updated is not None:
            languages = [lang for lang in languages if lang.id != updated.id]
            languages.append(updated)
        languages = sorted(languages, key=lambda x: x.lang_key)
        cache.set(SUPPORTED_LANGUAGES_CACHE_KEY, languages)


@receiver(post_save, sender=SupportedLanguages)
def post_save_lang(sender, instance, created, **kwargs):
    if created:
        sender.set_cached_languages(added=instance)
    else:
        sender.set_cached_languages(updated=instance)


@receiver(pre_delete, sender=SupportedLanguages)
def pre_delete_lang(sender, instance, **kwargs):
    sender.set_cached_languages(deleted=instance)


class TranslatedLang(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    lang = models.ForeignKey(SupportedLanguages, on_delete=models.CASCADE,)
    lang_key = models.CharField(max_length=7)
    _deflated_content = BinaryField()

    class TranslationExists(ValidationError): #thrown when translation with same value already exists
        def __init__(self, detail):
            super(TranslatedLang.TranslationExists, self).__init__(
                {'message': 'Translation label already exists', 'code': 2, 'detail': detail})


    class TranslationConflict(ValidationError):
        def __init__(self, key, old_value, new_value):
            super(TranslatedLang.TranslationConflict, self).__init__(
                {'message': 'Translation conflict for key %s. You have to edit this label.' % key, 'code': 0})
            self.old_value = old_value
            self.new_value = new_value

    class TranslationMalformed(ValidationError):#the translation passed does not contain sufficient data
        def __init__(self, detail):
            super(TranslatedLang.TranslationMalformed, self).__init__(
                {'message': 'Translation malformed', 'code': 1, 'additional_message': detail})

    class TranslationNotExists(ValidationError):#the translation passed does not contain sufficient data
        def __init__(self, key):
            super(TranslatedLang.TranslationNotExists, self).__init__(
                {'message': 'Translation language not exist key: %s' % key, 'code': 3})

    class TranslationValueParams(Exception):
        pass #the translation does not contain enough extra params '%s'

    @staticmethod
    @cached_in_request(params_key=lambda lang_key: 'TranslatedLang'+lang_key)
    def get_or_none(lang_key):
        try:
            return TranslatedLang.objects.get(lang_key = lang_key)
        except TranslatedLang.DoesNotExist:
            return None

    @staticmethod
    def make_label(name):
        value = str(name.strip().replace(' ','_').replace(':','').replace('__','_').replace('"','').replace("'",''))
        return value

    @staticmethod
    def add_translation(translation_dict, overwrite = False):
        try:
            name = translation_dict['name']
            lang_key = translation_dict['lang']
            value = translation_dict['value']
            if not value:
                raise TranslatedLang.TranslationMalformed('Label is empty.')
            if not TranslatedLang.validate_extraparams(name, value):
                raise TranslatedLang.TranslationMalformed('Not enough params in the label value.')
        except KeyError as ke:
            raise TranslatedLang.TranslationMalformed(ke)

        name =  TranslatedLang.make_label(name)
        tl = TranslatedLang.get_or_none(lang_key=lang_key)
        if not tl:
            raise TranslatedLang.TranslationNotExists(lang_key)

        tl.add_label(name, value, overwrite)
        tl.save()

    def add_label(self, name, value, overwrite = False):
        trans = self.translations
        if overwrite:
            trans[str(name)] = value
        else:
            try:
                orig_value = trans[str(name)]
                if orig_value == value:
                    raise TranslatedLang.TranslationExists('This label already exist.')
                else:
                    raise TranslatedLang.TranslationConflict(key=name, old_value=orig_value, new_value=value)
            except KeyError:
                trans[str(name)] = value
        self.translations = trans #this is needed so the property can get deflated

    @staticmethod
    def validate_extraparams(key, value):
        tl_orig = TranslatedLang.get_or_none(lang_key=USER_DEFAULT_LANG)
        try:
            orig_value = tl_orig.get_translation(key)
        except (KeyError, AttributeError):
            return True
        reg = re.compile(r'(%s|%\(\w+\)s)')
        orig = reg.findall(orig_value)
        new = reg.findall(value)
        if sorted(orig) == sorted(new):
            return True
        else:
            return False

    def __init__(self, *args, **kwargs):
        self._inflated_content = None
        super(TranslatedLang, self).__init__(*args, **kwargs)

    @property
    def translations(self):
        if self._inflated_content is None:
            if self._deflated_content:
                self._inflated_content = json.loads(zlib.decompress(self._deflated_content))
            else:
                self._inflated_content = {}
        return self._inflated_content

    @translations.setter
    def translations(self, trans_dict):
        self._inflated_content = trans_dict
        self._deflated_content = zlib.compress(json.dumps(self._inflated_content))

    @translations.deleter
    def translations(self):
        del self._inflated_content

    def get_translation(self, label):
        return self.translations[str(label)]

    def delete_translation(self, key):
        trans = self.translations
        try:
            value = trans.pop(key)
        except KeyError:
            value = trans.pop(str(key))
        self.translations = trans   #this step is necessary so the "property" magic can work and deflate the translations

        return value


class TranslatedImages(models.Model):
    lang = models.ForeignKey(SupportedLanguages, null=True, on_delete=models.DO_NOTHING)
    label = models.CharField(max_length=255, choices = images_labels)
    file = models.ForeignKey(UploadedFile, null=True, on_delete=models.DO_NOTHING)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)


class ImportTable(models.Model):
    lang = models.ForeignKey(SupportedLanguages, null=True, on_delete=models.DO_NOTHING)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    pasted_json = models.TextField(max_length=(1024 * 1024))
    added = models.TextField(max_length=(1024 * 1024))
    omitted = models.TextField(max_length=(1024 * 1024))
    conflict = models.TextField(max_length=(1024 * 1024))
    deflated_conflict = models.BinaryField(blank=True, null=True, default=None)
    conflict_rep = models.TextField(max_length=(1024 * 1024))
    deflated_conflict_rep = models.BinaryField(blank=True, null=True, default=None)
    not_valid = models.TextField(max_length=(1024 * 1024))
    create_notification = models.BooleanField(default=False, blank=True)
    notification_version = models.CharField(max_length=255, default='', blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)


class TranslationsSettings(SingletonModel):
    modified_date = models.DateTimeField(auto_now=True)
    notification_recipients = models.TextField(max_length=(1024 * 1024), default='', blank=True, null=True)


class NewsBase(models.Model):
    class Meta:
        abstract = True

    title = models.CharField(max_length=255, blank=False)
    short_text = models.TextField(blank=False)
    additional_text = models.TextField(blank=True)
    created_by = models.ForeignKey(User, related_name='%(app_label)s_%(class)s_created_by', null=True, on_delete=models.DO_NOTHING)
    # Fields for tracking creation date of post
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    year = models.IntegerField(blank=False)
    month = models.IntegerField(blank=False)
    day = models.IntegerField(blank=False)

    def __unicode__(self):
        return str(self.title)

    def __str__(self):
        return str(self).encode('utf-8')

class StatisticsBase(models.Model):
    class Meta:
        abstract = True

    statistics = models.TextField(null=True, blank=True, default=None)

class TranslationsNews(NewsBase):
    raw_text = models.TextField(blank=False)
    labels_count = models.IntegerField(default=0)


class TranslationsNewsStatistics(SingletonModel, StatisticsBase):
    pass


@receiver(post_save, sender=TranslatedImages)
def flush_translated_images_cache(sender, instance, **kwargs):
    from src.lorepo.translations.utils import get_translated_images
    get_translated_images.delete_cached(instance.lang)