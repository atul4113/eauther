from abc import ABCMeta, abstractmethod
import logging
from django.contrib.auth.models import User
from src.libraries.utility.helpers import get_object_or_none
from src.lorepo.filestorage.models import FileStorage
from src.lorepo.mycontent.models import Content, ContentType
from src.lorepo.public.util import send_message
from src.lorepo.user.models import UserProfile, UserLanguage
from src import settings
import xml.dom.minidom

from src.libraries.wiki.models import WikiPageTranslated


class BackendTaskConfig(object, metaclass=ABCMeta):
    max_retries_count = 5

    @abstractmethod
    def logic(self, results):
        pass

    @classmethod
    @abstractmethod
    def send_success(self, user, instance_name, subject='', body='', task_number = None):
        send_message(settings.SERVER_EMAIL, [user.email], subject, body)

    @classmethod
    @abstractmethod
    def send_failure(self, user, task_number, retry_number, instance_name, traceback, cursor=''):
        subject = '[%s] exception in task_number: %s retry_number: %s' % (instance_name, task_number, retry_number)
        body  = 'Coursor at: %s \nr'%cursor
        send_message(settings.SERVER_EMAIL, [user.email], subject, body + traceback.format_exc())

    @classmethod
    @abstractmethod
    def log_failure(self, instance_name, log):
        logging.error('[%s] log: %s' % (instance_name, log))

    @abstractmethod
    def get_queryset(self):
        pass


class UserProfileFixDB(BackendTaskConfig):

    def get_queryset(self):
        return User.objects.all()

    def logic(self, results):
        for user in results:
            profile, created = UserProfile.objects.get_or_create(user=user)
            user_language = get_object_or_none(UserLanguage, user=user)
            if user_language:
                if created and user_language.language_code != profile.language_code:
                    profile.language_code = user_language.language_code
                    profile.save()


class UserDjangaeFixDB(BackendTaskConfig):

    def get_queryset(self):
        return User.objects.all()

    def logic(self, results):
        for user in results:
            user.save() #creates special indexes for djangae purposes


class WikiPageTranslatedIndex(BackendTaskConfig):

    def get_queryset(self):
        return WikiPageTranslated.objects.all()

    def logic(self, results):
        for data in results:
            data.save()


def object_builder(class_name):
    try:
        return globals()[class_name]()
    except Exception:
        raise Exception('You need to implement class_name: %s and add it to function %s ' % (class_name, object_builder.__name__))


# search and list lessons that have corrupted main.xml:
# due to a bug in mAuthor, some lesson created had their the "theme.href" value entered under "useGrid" key
# in main.xml/interactiveContent/metadata/entry
class CorruptedLessonFinder(BackendTaskConfig):

    def get_queryset(self):
        return Content.objects.filter(is_deleted = False)[0:1000]

    def logic(self, results):
        from collections import OrderedDict
        self.broken_list = []
        for content in results:
            if content.content_type != ContentType.ADDON:
                error_type = ''
                template_name = ''
                template_id = ''
                template_url = ''
                #read XML
                try:
                    main_xml= xml.dom.minidom.parseString(content.file.contents)
                    corrupted = False
                    wrongEntry = None
                    wrongNode = None
                    rightEntry = None
                    #check for flaws
                    for e in main_xml.getElementsByTagName('entry'):
                        if e.getAttribute('value').startswith('/file/'):
                            if e.getAttribute('key') != 'theme.href':
                                wrongEntry = e.getAttribute('value')
                                wrongNode = e
                            else:
                                rightEntry = e.getAttribute('value')
                    if wrongEntry != None and wrongEntry != rightEntry:
                        corrupted = True
                        error_type = 'Template Error'
                        wrong_template_id = wrongEntry[6:]
                        try:
                            filestorage = FileStorage.objects.get(pk = wrong_template_id)
                            template = filestorage.history_for
                            suggested_name = ', SUGGESTED: %s VERSION %d' % (template.title.encode('utf-8', 'ignore'), filestorage.version)
                            suggested_url = ', SUGGESTED: %s/embed/%d' % (settings.BASE_URL, template.pk)
                        except Exception as e:
                            logging.error(e.message)
                            suggested_name = ', no suggestion'
                            suggested_url = ', no suggestion'
                        if rightEntry:
                            template_id = rightEntry[6:]
                            try:
                                filestorage = FileStorage.objects.get(pk=template_id)
                                template = filestorage.history_for
                                template_name = '%s VERSION %d' % (template.title.encode('utf-8', 'ignore'), filestorage.version) + suggested_name
                                template_url = '%s/embed/%d' % (settings.BASE_URL, template.pk) + suggested_url
                            except Exception as e:
                                logging.error(e.message)
                                template_name = "error"+suggested_name
                                template_url = "error"+suggested_url
                        else:
                            template_name = 'none' + suggested_name
                            template_url = 'none'+suggested_url
                except Exception as e:
                    logging.error(e.message)
                    corrupted = True
                    error_type = 'Corrupted XML'

                if corrupted:
                    #get author and company info
                    user_name = content.author.username
                    author_email = content.author.email
                    last_modified = str(content.modified_date)
                    content_spaces = content.contentspace_set.all()
                    spaces = [cs.space for cs in content_spaces if cs.space.is_corporate()]
                    publications = 'private space'
                    company_name = 'private space'
                    if len(spaces):
                        spaces_names = [space.title.encode('utf-8','ignore') for space in spaces]
                        publications = ','.join(spaces_names)
                        company_name = spaces[0].top_level.title.encode('utf-8', 'ignore')
                    #add to list/write to file
                    title = content.title.encode('utf-8', 'ignore')
                    self.broken_list.append(OrderedDict((
                        ('title', title),
                        ('href', '%s/embed/%d' % (settings.BASE_URL, content.pk)),
                        ('last_modified', last_modified),
                        ('username', user_name),
                        ('email', author_email),
                        ('publications', publications),
                        ('company', company_name.encode('utf-8', 'ignore')),
                        ('error_type', error_type),
                        ('current_template', template_name),
                        ('template_url', template_url)
                    )))

    def send_success(self, user, instance_name, subject='', body='', task_number=None):
        if task_number is None:
            super(CorruptedLessonFinder, self).send_success(user, instance_name, subject, body)
        elif len(self.broken_list):
            import src.cloudstorage as gcs
            import csv
            from src.lorepo.filestorage.utils import build_retry_params
            with gcs.open('%s/corrupted-lessons/success-%d.csv' % (settings.get_bucket_name('export-packages'), task_number), 'w', 'text/csv', retry_params=build_retry_params()) as f:
                w = csv.DictWriter(f, list(self.broken_list[0].keys()))
                w.writeheader()
                w.writerows(self.broken_list)

class ContentPaginationFixDB(BackendTaskConfig):

    def get_queryset(self):
        return Content.objects.all()

    def logic(self, results):
        for content in results:
            content.save(modified_date=False) #creates special indexes for djangae purposes
