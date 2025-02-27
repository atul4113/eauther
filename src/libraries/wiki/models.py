from django.contrib.auth.models import User
from django.db import models
from django.template.loader import render_to_string
from src.lorepo.filestorage.models import UploadedFile
import src.libraries.utility.cacheproxy as cache
from src.lorepo.mycontent.models import Content
from src.lorepo.util.searchable_models import Indexable
from src.markdown import markdown
from src.settings import USER_LANGUAGES, LANGUAGES

class WikiPage(models.Model):
    title = models.CharField(max_length=200)
    text = models.TextField()
    modified_date = models.DateTimeField(null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    is_toc = models.BooleanField(default=False)
    url = models.CharField(max_length=200)
    parent = models.ForeignKey('self', null=True, blank=True, related_name="kids", on_delete=models.DO_NOTHING)
    order = models.IntegerField(null=True)

    def __str__(self):
        return self.title


class PrivateAddonWikiPageManager(models.Manager):
    def get_or_create(self, defaults=None, **kwargs):
        try:
            return super(PrivateAddonWikiPageManager, self).get_or_create(defaults=defaults, **kwargs)
        except self.model.MultipleObjectsReturned:
            """
                WikiPage will be created on demand, so there can be more than one page in the database for the same 
                addon by eventual consistency.
                In this case, we want to return only the first page from the database.
            """
            lookup, _ = self._extract_model_params(defaults, **kwargs)
            return self.filter(**lookup).first(), False


class PrivateAddonWikiPage(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    text = models.TextField()
    addon = models.ForeignKey(Content, on_delete=models.DO_NOTHING)

    objects = PrivateAddonWikiPageManager()

    @staticmethod
    def get_default_text():
        return render_to_string('initdata/addon/addon.md').encode('utf-8')

    def get_page(self):
        return markdown(self.text)


class WikiPageTranslated(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(null=True)     #don't use the auto_now feature
    title = models.CharField(max_length=200)
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    is_toc = models.BooleanField(default=False)
    url = models.CharField(max_length=200)
    parent = models.ForeignKey('self', null=True, blank=True, related_name="kids", on_delete=models.DO_NOTHING)
    order = models.IntegerField(null=True)
    language_code = models.CharField(max_length=10, null=True)

    def __str__(self):
        return self.title


    def load_kids(self):
        self.loaded_kids = self.kids.filter(language_code='en').order_by('order')
        for p in self.loaded_kids:
            p.load_kids()


    @staticmethod
    def load_toc_kids(page_dict):
        page_dict['loaded_kids'] = []
        page_dict['loaded_kids'] = WikiPageTranslated.objects.filter(parent=page_dict['id'], language_code=page_dict['language_code'])
        page_dict['loaded_kids'] = page_dict['loaded_kids'].order_by('order').values('id', 'title', 'url', 'parent', 'order', 'is_toc', 'language_code')
        for pd in page_dict['loaded_kids']:
            WikiPageTranslated.load_toc_kids(pd)

    @staticmethod
    def translate_kids(toc, translated_toc, lang_code):
        for pd in toc:
            page = WikiPageTranslated.objects.filter(url=pd['url'], language_code=lang_code)
            page = page.values('id', 'title', 'url', 'parent', 'order', 'is_toc', 'language_code')[0]
            page['loaded_kids'] = []
            WikiPageTranslated.translate_kids(pd['loaded_kids'], page['loaded_kids'],  lang_code)
            translated_toc.append(page)

    @staticmethod
    def toc_pages(lang_code):
        if lang_code == 'en':
            toc_en = cache.get('wiki_pages_toc_en')
            if not toc_en:
                toc_en = WikiPageTranslated.objects.filter(parent=None, is_toc=True, language_code='en')
                toc_en = toc_en.order_by('order').values('id', 'title', 'url', 'parent', 'order', 'is_toc', 'language_code')
                for page_dict in toc_en:
                    WikiPageTranslated.load_toc_kids(page_dict)
                cache.set('wiki_pages_toc_en', toc_en)
            return toc_en
        else:
            toc = cache.get('wiki_pages_toc_%s' % (lang_code))
            if not toc:
                toc_en = WikiPageTranslated.toc_pages('en')
                toc = []
                WikiPageTranslated.translate_kids(toc_en, toc, lang_code)
                cache.set('wiki_pages_toc_%s' % (lang_code), toc)
            return toc


    @staticmethod
    def flush_toc():
        for lang in LANGUAGES:
             cache.delete('wiki_pages_toc_%s' % (lang[0]))

    @staticmethod
    def _pages_for_url(url):
        page_translations = cache.get("wiki_page_translated_%s"%(url))
        if not page_translations:
            page_translations = list(WikiPageTranslated.objects.filter(url=url))
            if page_translations:
                cache.set("wiki_page_translated_%s"%(url), page_translations)
        return page_translations

    @staticmethod
    def page_for_url(url, lang_code):
        page_translations = WikiPageTranslated._pages_for_url(url)
        for page in page_translations:
            if page.language_code == lang_code:
                return page
        return None

    @staticmethod
    def validated_language_code(lang_code=None, languages = USER_LANGUAGES):
        if not lang_code:
            return 'en'
        lang_codes = [lang[0] for lang in languages]
        return lang_code if lang_code in lang_codes else 'en'


    def clone_for_languages(self, lang_list=LANGUAGES):
        for language in lang_list: #omit 'en' which is always first
            if language[0] == self.language_code:
                continue #make sure we don't make copy of the default
            try:
                page_copy = WikiPageTranslated.objects.get(url = self.url, language_code = language[0])
            except WikiPageTranslated.DoesNotExist:
                page_copy = WikiPageTranslated(
                    url = self.url,
                    language_code = language[0],
                    title = self.title,
                    text = self.text,
                    modified_date=self.modified_date,
                    is_toc=self.is_toc
                )
                page_copy.author_id = self.author_id
                page_copy.save()

    def get_translations(self):
        try:
            return self._translations
        except AttributeError:
            page_translations = WikiPageTranslated._pages_for_url(self.url)
            self._translations = {}
            for page in page_translations:
                if page.id != self.id:
                    page.needs_update = True if page.modified_date <= self.modified_date else False
                    self._translations[page.language_code] = page
            self._translations[self.language_code] = self
        return self._translations


    def save(self, *args, **kwargs):
        if self.url:
            cache.delete("wiki_page_translated_%s"%(self.url))

        WikiPageTranslatedIndex(wiki_page_translated_entity=self).save()
        return super(WikiPageTranslated, self).save(*args, **kwargs)

    def delete(self, using=None):
        if self.url:
            cache.delete("wiki_page_translated_%s"%(self.url))
        WikiPageTranslatedIndex(wiki_page_translated_entity=self).delete()
        super(WikiPageTranslated, self).delete(using)


class WikiFile(models.Model):
    uploaded_file = models.ForeignKey(UploadedFile, null=True, on_delete=models.DO_NOTHING)


class WikiPageTranslatedIndex(Indexable):
    wiki_page_translated_entity = models.ForeignKey(WikiPageTranslated, null=True, blank=True, on_delete=models.CASCADE)

    _search_indexed_fields = ['title',
                              'text',
                              'is_toc',
                              'url',
                              'parent',
                              'order',
                              'language_code'
                              ]

    _search_indexed_tokenized_fields = ['title']

    _sorted_fields = ['title']

    def get_doc_id(self):
        if self.doc_id is None:
            self.doc_id = str(self.wiki_page_translated_entity.pk)
        return self.doc_id

    @property
    def title(self):
        return self.wiki_page_translated_entity.title

    @property
    def text(self):
        return self.wiki_page_translated_entity.text

    @property
    def is_toc(self):
        return self.wiki_page_translated_entity.is_toc

    @property
    def url(self):
        return self.wiki_page_translated_entity.url

    @property
    def parent(self):
        return self.wiki_page_translated_entity.parent

    @property
    def order(self):
        return self.wiki_page_translated_entity.order

    @property
    def language_code(self):
        return self.wiki_page_translated_entity.language_code
