# -*- coding: utf-8 -*-
import logging

from djangae.contrib.pagination import paginated_model
from djangae.fields import ListField
from django.contrib.auth.models import User
from django.core.exceptions import MultipleObjectsReturned
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import get_object_or_404
from src.lorepo.filestorage.models import FileStorage
from src.lorepo.labels.models import Label
from src.lorepo.mycontent.signals import content_updated, template_updated
from src.lorepo.spaces.models import Space
import datetime
import xml.dom.minidom
import re
import src.libraries.utility.cacheproxy as cache
import xml.etree.ElementTree as ET

from src.lorepo.util.Mixins.ModelCacheMixin import ModelCacheMixin
from src.mauthor.utility.utils import sanitize_title
from src.xml_parsers.explicit_parsers.add_titile_to_lesson_parser import AddTitleToXMLParser
from src.xml_parsers.explicit_parsers.lesson_copy_parser import LessonCopyParser
from src.xml_parsers.explicit_parsers.get_template_parser import GetTemplateParser


class ContentType():
    LESSON = 1
    TEMPLATE = 2
    ADDON = 3

class Asset(models.Model):
    href = None
    content_type = None
    title = None
    file_name = None

    def __init__(self, node):
        '''Creates asset out of XML node'''
        self.href = node.getAttribute("href")
        self.content_type = node.getAttribute("contentType")
        self.title = node.getAttribute("title")
        self.file_name = node.getAttribute("fileName")
        self.type = node.getAttribute("type")

    def get_file_id(self):
        if '/file/serve/' in self.href:
            try:
                return int(self.href.replace('/file/serve/', ''))
            except ValueError:
                return None
        return None


@paginated_model(orderings=[
    "modified_date",
    "title"
])
class Content(models.Model, ModelCacheMixin):
    version = models.IntegerField(default=0) #version attribute for big fixdb purposes
    title = models.CharField(max_length=200, default='Content')
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField() #field is changed automatically in save method, caused by customfidb purposes
    is_public = models.BooleanField(default=False)
    is_template = models.BooleanField(default=False)
    content_type = models.IntegerField(choices=[(ContentType.LESSON, 'lesson'), (ContentType.TEMPLATE, 'template'), (ContentType.ADDON, 'addon')], default=1)
    is_featured = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    author = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    file = models.ForeignKey(FileStorage, on_delete=models.DO_NOTHING)
    public_version = models.OneToOneField(FileStorage, null=True, blank=True, related_name='public_version_for', on_delete=models.DO_NOTHING)
    icon_href = models.CharField(max_length=255, default=None, null=True)
    big_icon_href = models.CharField(max_length=255, default=None, null=True)
    tags = models.TextField(max_length=2048, null=True, blank=True)
    description = models.TextField(max_length=2048, null=True, blank=True)
    short_description = models.TextField(null=True, blank=True)
    view_count = models.IntegerField(default=0)  # Not used at the moment, legacy flag from src.lorepo.com
    associated_content = models.ForeignKey('self', null=True, blank=True, on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=255, default=None, null=True)
    is_globally_public = models.BooleanField(default=False)
    spaces_path = models.CharField(max_length=250, default='')
    spaces = ListField(models.CharField()) # this field is type string ! remember about it when filtering
    passing_score = models.IntegerField(default=0)
    original = models.ForeignKey('self', null=True, blank=True, related_name='original_for', on_delete=models.DO_NOTHING)
    xliff_file = models.OneToOneField(FileStorage, null=True, blank=True, related_name='xliff_for', on_delete=models.DO_NOTHING)
    enable_page_metadata = models.BooleanField(default=False)

    CACHE_PREFIX = "content_%s"

    class ContentNotSaved(Exception):
        pass

    def __str__(self):
        return str(self).encode('utf-8')

    def __unicode__(self):
        return '%s' % (self.title,)

    @staticmethod
    def get_cached_or_none(id):
        try:
            return Content.get_cached(id)
        except Content.DoesNotExist:
            return None

    @staticmethod
    def get_cached_or_404(id):
        try:
            return Content.get_cached(id)
        except Content.DoesNotExist:
            raise Http404()

    @staticmethod
    def get_cached(id, timeout=30*60):
        content = cache.get(Content.CACHE_PREFIX %(str(id)))
        if content:
            return content
        else:
            content = Content.objects.get(id=id)
            cache.set(Content.CACHE_PREFIX %(str(id)), content, timeout=timeout)
            return content

    def is_content_public(self):
        try:
            is_pub = self.public_version is not None and self.is_public
        except FileStorage.DoesNotExist:
            is_pub = False
        return is_pub

    def makeCopy(self, should_name_copy, new_author, pages_to_extract = []):
        now = datetime.datetime.now()

        if self.content_type in [ContentType.LESSON, ContentType.TEMPLATE]:
            contentFile = self._lesson_copy(new_author, now, pages_to_extract)

        elif self.content_type == ContentType.ADDON:
            contentFile = self._addon_copy(new_author, now)

        else:
            logging.warning("Undefined content_type %d %d", self.id, self.content_type)

        if should_name_copy:
            title = 'Copy of ' + self.title
        else:
            title = self.title

        # save new content 
        copy = Content(
                       title = title,
                       created_date = now,
                       modified_date = now,
                       author = new_author,
                       icon_href = self.icon_href,
                       file = contentFile,
                       tags = self.tags,
                       description = self.description,
                       short_description = self.short_description,
                       content_type = self.content_type
                       )
        copy.save()

        contentFile.history_for = copy
        contentFile.version = 1
        contentFile.save()
        return copy

    def _lesson_copy(self, new_author, created_date, pages_to_extract):
        lesson_copy_handler = LessonCopyParser(new_author=new_author, pages_to_extract=pages_to_extract)
        file_storage_entry = self.file

        with file_storage_entry as content_file:
            lesson_copy_handler.parse(content_file)

        # Create new content file
        contentFile = FileStorage(
                           created_date = created_date,
                           modified_date = created_date,
                           content_type = "text/xml",
                           contents = lesson_copy_handler.get_output_value(),
                           owner = new_author)
        contentFile.save()
        return contentFile

    def _addon_copy(self, new_author, created_date):
        contentFile = FileStorage(
                           created_date = created_date,
                           modified_date = created_date,
                           content_type = "text/xml",
                           contents = self.file.contents,
                           owner = new_author)
        contentFile.save()
        return contentFile

    def _modify_addon(self, contentFile, content):
        doc = xml.dom.minidom.parseString(self.file.contents)
        for node in doc.getElementsByTagName("presenter"):
            node.firstChild.nodeValue = re.sub('Addon\d+_create', 'Addon%(id)s_create' % {'id' : content.id}, node.firstChild.nodeValue)

        for node in doc.getElementsByTagName("addon"):
            node.setAttribute("id", str(content.id))

        contentFile.contents = doc.toxml("utf-8")
        contentFile.save()
        return contentFile

    def get_template(self):
        template = cache.get("content_template_%s" % self.id)
        if template:
            return template
        template = None

        try:
            get_template_handler = GetTemplateParser()
            content_file = self.file

            with content_file as file_contents:
                get_template_handler.parse(file_contents)

            value = get_template_handler.get_entry_attr()

            if value != '':
                splitted_value = value.split('/')
                if len(splitted_value) == 3:
                    file_id = int(splitted_value[2])
                    fses = FileStorage.objects.filter(pk=file_id)
                    fs = fses[0] if len(fses) > 0 else None
                    if fs:
                        template = fs.history_for
                        if template:
                            cache.set("content_template_%s" % self.id, template, 60 * 60 * 24)

        except Exception as e:
            pass

        return template

    def getAssets(self, content_type=None):
        doc = xml.dom.minidom.parseString(self.file.contents)
        assets = []
        for node in doc.getElementsByTagName("asset"):
            assets.append(Asset(node))

        return assets

    def getHeight(self):
        height = "600"
        pattern = re.compile(r'height[\s]*\:[\s]*(?P<w>\d+)px')
        match = pattern.search(self.file.contents)
        if match:
            height = match.group('w')
        return height

    def getWidth(self):
        width = "800"
        pattern = re.compile(r'width[\s]*\:[\s]*(?P<w>\d+)px')
        match = pattern.search(self.file.contents)
        if match:
            width = match.group('w')
        return width

    def get_pages(self):
        pages = []
        doc = xml.dom.minidom.parseString(self.file.contents)
        for node in doc.getElementsByTagName("page"):
            href = node.getAttribute("href")
            href = re.findall('\d+', href)[0]
            pages.append(get_object_or_404(FileStorage, pk=href))
        return pages

    def get_pages_data(self):
        data = []
        tree = ET.fromstring(self.file.contents)
        for node in tree.iter('page'):
            if node.get('name') not in ['header', 'footer']:
                page = {
                    'id' : node.get('id'),
                    'title' : node.get('name'),
                    'href' : node.get('href')
                    }
                data.append(page)
        return data

    def get_page_titles(self):
        titles = []
        doc = xml.dom.minidom.parseString(self.file.contents)
        for node in doc.getElementsByTagName("page"):
            if not node.parentNode.hasAttribute("name") and node.parentNode.nodeName != 'folder':
                name = node.getAttribute("name")
                titles.append(name)
        return titles


    def get_metadata(self):
        return {'title' : self.title,
                'tags' : self.tags,
                'description' : self.description,
                'short_description' : self.short_description
                }

    def set_metadata(self, metadata):
        self.title = sanitize_title(metadata['title']).strip(' ')
        self.tags = metadata['tags'].strip(' \t\n\r')
        self.description = metadata['description'].strip(' \t\n\r')
        self.short_description = metadata['short_description'].strip(' \t\n\r')

    def add_title_to_xml(self):
        add_title_to_xml_handler = AddTitleToXMLParser(self.title)
        file_entry = self.file

        with file_entry as content_file:
            if self.who_is_editing() is None:
                add_title_to_xml_handler.parse(content_file)

                if add_title_to_xml_handler.count > 0:
                    self.file.contents = add_title_to_xml_handler.get_output_value()
                    self.file.save()

    def get_score_type(self):
        doc = xml.dom.minidom.parseString(self.file.contents)
        ics = doc.getElementsByTagName('interactiveContent')
        ic = ics[0] if len(ics) > 0 else None
        return ic.getAttribute('scoreType') if ic and ic.hasAttribute('scoreType') else 'last'

    def set_score_type(self, score_type):
        doc = xml.dom.minidom.parseString(self.file.contents)
        ic = doc.getElementsByTagName('interactiveContent')[0]
        ic.setAttribute('scoreType', score_type)
        self.file.contents = doc.toxml(encoding='utf-8')
        self.file.save()

    def set_user_is_editing(self, user):
        if self.pk is None:
            raise Content.ContentNotSaved('Cannot set edit lock on not saved content.')
        CurrentlyEditing.objects.filter(content=self).delete()
        self._edit_lock = CurrentlyEditing(content=self, user=user)
        self._edit_lock.save()

        try:
            CurrentlyEditing.set_cache(self.pk, self._edit_lock)
        except ValueError:
            # reload lock from DB to prevent pickle extended objects
            self._edit_lock = CurrentlyEditing.objects.get(pk=self._edit_lock.id)
            CurrentlyEditing.set_cache(self.pk, self._edit_lock)

        Content.set_cache(self.id, self, 30*60)

    def who_is_editing(self):
        try:
            return self._edit_lock.user
        except:
            pass
        try:
            self._edit_lock = CurrentlyEditing.get_cache(self.pk)
            return self._edit_lock.user
        except:
            pass
        try:
            self._edit_lock = CurrentlyEditing.objects.get(content=self)
            CurrentlyEditing.set_cache(self.pk, self._edit_lock)
            return self._edit_lock.user
        except MultipleObjectsReturned:
            ces = CurrentlyEditing.objects.filter(content=self)
            self._edit_lock = ces[0]
            for cs in ces[1:]:
                cs.delete()
            CurrentlyEditing.set_cache(self.pk, self._edit_lock)
            return self._edit_lock.user
        except:
            pass
        return None

    def stop_editing(self, user):
        CurrentlyEditing.cache_delete(self.pk)
        CurrentlyEditing.objects.filter(content=self, user=user).delete()
        self._edit_lock = None
        Content.set_cache(self.id, self)

    def save(self, modified_date=True, *args, **kwargs):
        if modified_date: #usefull for customfixdb purposes i.e to not modify this field on update
            self.modified_date = datetime.datetime.now()

        super(Content, self).save(*args, **kwargs)
        Content.set_cache(self.id, self)
        content_updated.send(sender=None, content_id=self.id, content_type=self.content_type)
        if self.content_type == ContentType.TEMPLATE and len(self.spaces) > 0:
            template_updated.send(sender=None, company_id=self.spaces[0])

    def delete(self, using=None):
        Content.cache_delete(self.id)
        super(Content, self).delete(self, using)

    @staticmethod
    @receiver(post_save, sender=FileStorage)
    def content_changed(sender, instance, **kwargs):
        Content.cache_delete(instance.history_for_id)

class ContentAccess(models.Model):
    """
    Prawa dostępu do contentu
    1 - read
    2 - write
    3 - owner
    """
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    content = models.ForeignKey(Content, on_delete=models.DO_NOTHING)
    access_right = models.IntegerField(choices=[(1, 'read'), (2, 'write'), (2, 'owner')],default=3)
    is_deleted = models.BooleanField(default=False)
    modified_date = models.DateTimeField(null=True)

    class Meta:
        ordering = ('-modified_date',)
    
    def __str__(self):
        return self.content.title


class ContentLabels(models.Model):
    """
    Zawiera połączenie contentu z etykietami
    """
    content = models.ForeignKey(Content, on_delete=models.DO_NOTHING)
    content_access = models.ForeignKey(ContentAccess, null=True, on_delete=models.DO_NOTHING)
    label = models.ForeignKey(Label, on_delete=models.DO_NOTHING)


class ContentSpace(models.Model):
    content = models.ForeignKey(Content, on_delete=models.DO_NOTHING)
    space = models.ForeignKey(Space, on_delete=models.DO_NOTHING)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return '%(content)s:%(space)s' % {'content' : self.content.title, 'space' : self.space.title}

        
class ContentLike(models.Model):
    content = models.ForeignKey(Content, on_delete=models.DO_NOTHING)
    ip = models.CharField(max_length=32, unique=True)
    like = models.BooleanField()
    date = models.DateTimeField()
    rating = models.FloatField(null=True)

    def __str__(self):
        return self.ip


class AddonCategory(models.Model):
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class AddonToCategory(models.Model):
    addon = models.ForeignKey(Content, on_delete=models.DO_NOTHING)
    category = models.ForeignKey(AddonCategory, on_delete=models.DO_NOTHING)

    def __str__(self):
        return '%(addon)s:%(category)s' % {'addon' : self.addon.title, 'category' : self.category.title}


class SpaceTemplate(models.Model):
    space = models.ForeignKey(Space, null=True, blank=True, on_delete=models.DO_NOTHING)
    template = models.ForeignKey(Content, on_delete=models.DO_NOTHING)


class CurrentlyEditing(models.Model, ModelCacheMixin):
    content = models.ForeignKey(Content, on_delete=models.DO_NOTHING)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    edited_since = models.DateTimeField(auto_now_add=True)

    CACHE_PREFIX = "content_edited_%s"

    def __str__(self):
        return '%(username)s:%(content)s' % {'username' : self.user.username, 'content' : self.content.title}


class DefaultTemplate(models.Model):
    template = models.ForeignKey(Content, on_delete=models.DO_NOTHING)


class UpdateTemplateStatus():
    UPDATED = 0
    NO_TEMPLATE = 1
    CONTENT_CURRENTLY_EDITED = 2
    TEMPLATE_CURRENTLY_EDITED = 3


class RecentlyOpened(models.Model):
    created_date = models.DateTimeField(auto_now=True)
    content = models.ForeignKey(Content, on_delete=models.DO_NOTHING)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
