import json
import re
from django.http import HttpRequest
from django.template.defaultfilters import striptags
from django.utils.safestring import mark_safe
from src import settings
from src.lorepo.filestorage.models import UploadedFile


BASE_URL = settings.BASE_URL
USER_DEFAULT_LANG = 'en_US'


def get_sys_label(*args, **kwargs):
    return ''


class MetaSEO(object):
    request = None
    kwargs = None
    default_type = 'website'
    fb_app_id = '1475109026125723'
    og_args = ['url', 'type', 'title', 'description']
    default_image = {
        'url': '/media/images/mauthor_logo.png',
        'width': 429,
        'height': 121
    }

    def __init__(self, request, **kwargs):
        self.request = request
        self.kwargs = kwargs

    def get_title(self):
        if 'title' in self.kwargs:
            return self.kwargs['title']
        if 'title_label' in self.kwargs:
            return get_sys_label(self.request, self.kwargs['title_label'], self.kwargs.get('title_params'))\
                .decode('utf-8')
        return "eAuthor - Create once, publish many"

    def get_url(self):
        return self.kwargs.get('url', BASE_URL + self.request.path)

    def get_type(self):
        return self.kwargs.get('type', self.default_type)

    def get_image_url(self):
        if 'image_id' in self.kwargs and self.kwargs['image_id'] is not None:
            return "%s/file/serve/%s" % (BASE_URL, self.kwargs['image_id'])
        elif 'image_url' in self.kwargs and self.kwargs['image_url'] is not None:
            return self.kwargs.get('image_url')
        elif 'image' in self.kwargs and self.kwargs['image'] is not None:
            return "%s%s" % (BASE_URL, self.kwargs['image'])
        else:
            return BASE_URL + self.default_image['url']

    def get_description(self):
        if 'description' in self.kwargs:
            return self.kwargs['description']
        if 'description_label' in self.kwargs:
            return get_sys_label(self.request, self.kwargs['description_label'], self.kwargs.get('description_params'))\
                .decode('utf-8')
        return 'mAuthor, a Multiplatform ePublishing Solution that enables you to create highly interactive content ' \
               'once for all kinds of devices, screen resolutions and operating systems.'

    def get_keywords(self):
        return self.kwargs.get('keywords')

    def title_html(self):
        return '<title>%s</title>' % striptags(self.get_title())

    def link_html(self):
        return '<link rel="canonical" href="%s" />' % self.get_url()

    def meta_html(self, name, content):
        return '<meta name="%s" content="%s" />' % (name, striptags(content))

    def og_html(self, name, content):
        return '<meta property="og:%s" content="%s" />' % (name, striptags(content))

    def fb_app_id_html(self):
        return '<meta property="fb:app_id" content="%s" />' % self.fb_app_id

    def image_og_html(self):
        elements = []
        image_url = self.get_image_url()
        elements.append(self.og_html('image', image_url))
        if image_url == BASE_URL + self.default_image['url']:
            elements.append(self.og_html('image:width', self.default_image['width']))
            elements.append(self.og_html('image:height', self.default_image['height']))
        if 'image_width' in self.kwargs and 'image_height' in self.kwargs:
            elements.append(self.og_html('image:width', self.kwargs['image_width']))
            elements.append(self.og_html('image:height', self.kwargs['image_height']))
        else:
            try:
                # Extract file id from image_url if possible
                match = re.search(r'/file/serve/(\d+)', image_url)
                image_file = None
                if match:
                    image_id = match.group(1)
                    from src.lorepo.filestorage.models import UploadedFile
                    image_file = UploadedFile.objects.filter(id=image_id).first()
                if image_file:
                    if not image_file.meta:
                        image_file.calculate_uploaded_image_meta()
                        image_file.save()
                    meta = json.loads(image_file.meta)
                    elements.append(self.og_html('image:width', meta['width']))
                    elements.append(self.og_html('image:height', meta['height']))
            except ValueError:
                pass

        return mark_safe('\n'.join(elements))

    def __unicode__(self):
        elements = [
            self.link_html(),
            self.title_html(),
            self.meta_html("description", self.get_description())
            ]
        if self.get_keywords():
            elements.append(self.meta_html("keywords", self.get_keywords()))
        for arg in self.og_args:
            elements.append(self.og_html(arg, getattr(self, 'get_%s' % arg)()))
        elements.append(self.image_og_html())
        elements.append(self.fb_app_id_html())
        return mark_safe('\n'.join(elements))

    def __str__(self):
        return self.__unicode__()

    def __bool__(self):
        return isinstance(self.request, HttpRequest)