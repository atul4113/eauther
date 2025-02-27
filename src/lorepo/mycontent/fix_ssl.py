# coding=utf-8
import logging
import xml

import datetime

from django.shortcuts import get_object_or_404
from django.utils.safestring import mark_safe
from django.views.generic import TemplateView
from src.libraries.utility.decorators import cached_property
from src.lorepo.filestorage.models import FileStorage, UploadedFile
from src.lorepo.spaces.models import SpaceType, Space
from src.mauthor.utility.decorators import LoginRequiredMixin

try:
    from lxml import etree
except ImportError:
    logging.error('\n%s\n!!! lxml is not installed on your computer\n'
                  '!!! Download it from: http://www.lfd.uci.edu/~gohlke/pythonlibs/#lxml\n%s' % ('!'*90, '!'*90))


class ContentException(Exception):
    pass


def update_property(p):
    changed = False
    value = p.get('value')
    if 'http:' == value[:5]:
        p.set('value', value[5:])
        changed = True
    if 'https:' == value[:6]:
        p.set('value', value[6:])
        changed = True
    return changed


def fixSwiffyAnimation(swiffy):
    changed = False
    for e in swiffy.findall(".//properties/property[@name='Animations']/items/item/property[@name='swiffyobject']"):
        updated = update_property(e)
        changed = changed or updated
    return changed


def fix_file_properties(addon):
    changed = False
    for e in addon.findall(".//properties/property[@type='file']"):
        updated = update_property(e)
        changed = changed or updated
    return changed


def fixIframe(addon):
    changed = False
    for e in addon.findall(".//properties/property[@name='iframeURL']"):
        updated = update_property(e)
        changed = changed or updated
    for e in addon.findall(".//properties/property[@name='index']"):
        updated = update_property(e)
        changed = changed or updated
    return changed


ADDONS_FIXERS = {
    'SwiffyAnimation': fixSwiffyAnimation,
    'Viewer_3D': fix_file_properties,
    'Paragraph': fix_file_properties,
    'Paragraph_Keyboard': fix_file_properties,
    'Iframe': fixIframe
}


def fix_page_data(page):
    root = etree.XML(page.contents)
    changed = False
    for addonID, fixer in list(ADDONS_FIXERS.items()):
        for entry in root.findall(".//modules/addonModule[@addonId='%s']" % addonID):
            fixed = fixer(entry)
            changed = changed or fixed
    if changed:
        page.contents = etree.tostring(root)
    return changed


def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)


def remove_css_comments(text):
    text = text.strip()
    while True:
        start = text.find(r'/*')
        if start == -1:
            break
        end = text.find(r'*/', start)
        if end == -1:
            substring = text[start:]
        else:
            substring = text[start:end+2]
        text = text.replace(substring, '')
    return text.strip()


class ContentFixer(object):

    def __init__(self, content, user=None):
        self.content = content
        self.user = user

    @cached_property
    def pages_to_fix(self):
        pages = []
        for index, page in enumerate(self.content.get_pages()):
            if fix_page_data(page):
                pages.append(str(index))
        return pages

    def check_styles(self):
        doc = xml.dom.minidom.parseString(self.content.file.contents)
        styles = doc.getElementsByTagName("style")
        if not styles:
            return False
        style = styles[0]
        style_text = getText(style.childNodes)
        style_text = remove_css_comments(style_text)
        return (style_text.find('https://') != -1) or (style_text.find('http://') != -1)

    def check_external_resources(self):
        fix_pages = bool(self.pages_to_fix)
        fix_styles = self.check_styles()
        if not (fix_pages or fix_styles):
            return {
                'status': 0,
                'message': 'Content %s doesn\'t have external resources' % str(self.content)
            }
        return {
            'status': 1,
            'id': self.content.id,
            'content_id': self.content.file_id,
            'title': str(self.content),
            'fix_styles': int(fix_styles),
            'fix_pages': ','.join(self.pages_to_fix)
        }

    def check_is_content_edited(self):
        editor = self.content.who_is_editing()
        if editor is not None:
            raise ContentException('User %s is currently editing %s.' % (editor, self.content))

    """
    def make_schemeless(self):
        doc = xml.dom.minidom.parseString(self.content.file.contents)
        pages = doc.getElementsByTagName("page")
        for index in self.pages_to_fix:
            new_page = pages[index]
            href = new_page.getAttribute("href")
            href = re.findall('\d+', href)[0]
            page_to_update = FileStorage.objects.get(pk=href)
            if fix_page_data(page_to_update):
                page_to_update.save()

    def fix(self):
        check = self.check_external_resources()
        if check['status'] == 0:
            raise ContentException(check['message'])
        self.check_is_content_edited()
        self.content.modified_date = datetime.datetime.now()
        self.content.file = create_new_version(self.content.file, self.user, comment='schemeless_fix', shallow=False)
        self.content.save()
        self.make_schemeless()
    """


class SslReportView(LoginRequiredMixin, TemplateView):
    template_name = 'mycontent/ssl_report.html'
    space_type = None

    def get_context_data(self, **kwargs):
        preview = 'mycontent/view'
        if self.space_type is SpaceType.CORPORATE:
            preview = 'corporate/view'
        space = get_object_or_404(Space, pk=kwargs.get('space_id'))
        file = get_object_or_404(UploadedFile, pk=kwargs.get('file_id'))
        lessons = []
        templates = []
        summary = []
        contents = file.gcs_handler().read()
        flag = None
        for line in contents.split('\n'):
            line = line.strip()
            if '--Templates--' == line:
                flag = 'T'
                continue
            if '--Lessons--' == line:
                flag = 'L'
                continue
            if '--Summary--' == line:
                flag = 'S'
                continue
            if flag is 'S':
                summary.append(line)
                continue
            row = line.split('\t')
            entry = {
                'id': row[0],
                'content_id': row[1],
                'fix_styles': int(row[2]),
                'fix_pages': row[3],
                'title': row[4],
            }
            if flag is 'T':
                templates.append(entry)
            elif flag is 'L':
                lessons.append(entry)

        return {
            'superuser': self.request.user.is_superuser,
            'preview': preview,
            'space': space,
            'lessons': lessons,
            'templates': templates,
            'summary': mark_safe('<br />'.join(summary)),
        }
