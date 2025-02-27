import json
import re
import logging

import datetime

import zlib

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, \
    HttpResponsePermanentRedirect, HttpResponseRedirect
from django.template.loader import render_to_string
from itertools import islice

import settings
from src.libraries.utility.decorators import backend
from src.lorepo.public.util import send_message
from src.lorepo.translations.utils import save_translated_image_to_cache, change_session_lang, \
    get_sys_label, get_user_lang, delete_cache_translated_image, get_static_language, get_safely_translation, \
    delete_cached_language
from src.lorepo.translations.models import SupportedLanguages, \
    TranslatedImages, TranslationsNewsStatistics, TranslatedLang, ImportTable, TranslationsNews, TranslationsSettings
from src.lorepo.util.singleton_model import SingletonModel
from settings import USER_DEFAULT_LANG, SERVER_EMAIL, APP_NAME
from django.contrib.auth.models import User
from django.core.mail import mail_admins
from django.template import loader, Context, RequestContext
from django.contrib import messages
from src.libraries.utility.environment import get_versioned_module, get_app_version
from django.utils.html import escape

def send_confirmation(user, lang_key):
    subject = get_safely_translation('lorepo.translations.views.add_lang_confirm', get_user_lang(user), lang_key)
    context = Context({'lang_key': lang_key, 'user': user, 'app_name': APP_NAME})
    email = loader.get_template('translations/confirmation.txt')
    rendered = email.render(context)
    send_message(SERVER_EMAIL, [user.email], subject, rendered)


def send_failure_notification(user, lang_key=None):
    subject = get_safely_translation('lorepo.translations.views.add_lang_fail', get_user_lang(user), (lang_key or ''))
    context = Context({'lang_key': lang_key or '', 'user': user, 'app_name': APP_NAME})
    email = loader.get_template('translations/creating_failure.txt')
    rendered = email.render(context)
    send_message(SERVER_EMAIL, [user.email], subject, rendered)

@backend
def add_language_async(request, lang_id, user_id):
    user = get_object_or_404(User, pk=user_id)
    lang = get_object_or_404(SupportedLanguages, pk=lang_id)
    lang_key = lang.lang_key

    try:
        default_lang = SupportedLanguages.objects.get(lang_key=USER_DEFAULT_LANG)
        tl_orig = TranslatedLang.get_or_none(default_lang.lang_key)
        tl_new = TranslatedLang.get_or_none(lang.lang_key)
        if tl_new is not None:
            raise Exception('TranslationsLang for new laguage already exists!')
        else:
            tl_new = TranslatedLang(lang = lang, lang_key= lang.lang_key)
            if tl_orig is not None:
                tl_new.translations = tl_orig.translations
            tl_new.save()
        default_images = TranslatedImages.objects.filter(lang=default_lang)
        for img in default_images:
            # Creating a copy of translated image file
            image_file = img.file
            image_file.pk = None
            image_file.save()

            new_image = TranslatedImages(
                file=image_file,
                lang=lang,
                label=img.label
            )
            new_image.save()

            save_translated_image_to_cache(new_image.label, lang.lang_key, image_file)
        send_confirmation(user, lang_key)
    except Exception:
        import traceback
        import logging
        logging.exception('Language creation failed')
        mail_admins('Language creation failed', traceback.format_exc())
        send_failure_notification(user, lang_key)

    return HttpResponse('ok')

def send_conflict_request(url, user):
    subject = get_safely_translation('lorepo.translations.views.conflict_request', get_user_lang(user))
    context = Context({'user': user, 'url': url, 'BASE_URL': settings.BASE_URL})
    email = loader.get_template('translations/conflict_request.txt')
    rendered = email.render(context)
    send_message(SERVER_EMAIL, [user.email], subject, rendered)

def send_import_summary(user, log):
    subject = get_safely_translation('lorepo.translations.views.Import_completed', get_user_lang(user))
    context = Context({'user': user, 'import': log})
    email = loader.get_template('translations/import_summary.txt')
    rendered = email.render(context)
    send_message(SERVER_EMAIL, [user.email], subject, rendered)

def fill_news_info(news, user):
    today = datetime.date.today()

    news.created_by = user
    news.year = today.year
    news.month = today.month
    news.day = today.day


def update_news_statistics(entity_class, news, **kwargs):
    if issubclass(entity_class, SingletonModel):
        news_statistics = entity_class.load()
    else:
        news_statistics, _ = entity_class.objects.get_or_create(**kwargs)

    updated_statistics = _update_news_info(news_statistics.statistics, news)
    news_statistics.statistics = updated_statistics
    news_statistics.save()


def create_or_edit_translations_notification(labels, user, user_lang, news=None, version=None):
    if not labels:
        raise Exception()

    short_text_json = json.loads("{" + labels + "}")
    labels_count = len(list(short_text_json.keys()))
    short_text_modified = ''
    additional_text = ''
    title = get_safely_translation('translations.add_notification.title_prefix', user_lang) + " "
    title += version if version else str(get_app_version())

    for key in list(islice(list(short_text_json.keys()), 10)):
        short_text_modified += '<a href="/panel/translations/%s">"%s"</a><br/>' % (key, key)

    for label in short_text_json:
        additional_text += '<a href="/panel/translations/%s">"%s": "%s"</a><br/>' % \
                               (label, label, escape(short_text_json[label]))

    send_notificaiton = False
    if news is None:
        news = TranslationsNews(title=title)
        fill_news_info(news, user)
        send_notificaiton = True

    news.short_text = short_text_modified
    news.labels_count = labels_count
    news.raw_text = labels
    news.additional_text = additional_text

    news.save()

    if send_notificaiton:
        update_news_statistics(TranslationsNewsStatistics, news)
        _send_notification_added_mail(news)

@backend
def import_translations_step2(request, space_id=None):
    my_import = get_object_or_404(ImportTable, pk=space_id)
    my_json = json.loads(my_import.pasted_json)
    log = {'added': [], 'conflict': [], 'omitted': [], 'not_valid': []}
    tls = []
    tl = None
    for tl_temp in TranslatedLang.objects.all():
        if tl_temp.lang_key == my_import.lang.lang_key:
            tl = tl_temp
        else:
            tls.append(tl_temp)
    if tl is None:
        tl = TranslatedLang(lang = my_import.lang, lang_key=my_import.lang.lang_key)
        tl.save()

    for name, value in list(my_json.items()):
        try:
            if not value:
                raise TranslatedLang.TranslationMalformed('Label is empty.')
            if not TranslatedLang.validate_extraparams(name, value):
                raise TranslatedLang.TranslationMalformed('Not enough params in the label value.')
            name = TranslatedLang.make_label(name)
            tl.add_label(name, value)
            log['added'].append(name)
            for tl_temp in tls:
                try:
                    tl_temp.add_label(name, value)
                except Exception:
                    pass
        except  TranslatedLang.TranslationExists:
            log['omitted'].append("%s = \"%s\"" % (name, value))
        except TranslatedLang.TranslationConflict as e:
            conflict = {
                'lang_key': tl.lang_key,
                'name': name,
                'old_value': e.old_value,
                'new_value': e.new_value
            }
            log['conflict'].append(conflict)

        except Exception:
            logging.exception('Add label error')
            log['not_valid'].append("%s = \"%s\"" % (name, value))

    tl.save()
    for tl_temp in tls:
        tl_temp.save()

    my_import.added = json.dumps(log['added'])
    my_import.deflated_conflict = zlib.compress(json.dumps(log['conflict']))
    my_import.omitted = json.dumps(log['omitted'])
    my_import.not_valid = json.dumps(log['not_valid'])
    my_import.save()

    if json.dumps(log['conflict']) != '[]':
        url = '/panel/translations/import/3/%s' % my_import.id
        send_conflict_request(url, my_import.user)
    else:
        if my_import.create_notification:
            create_or_edit_translations_notification(my_import.pasted_json[1:-1], my_import.user,
                                                     get_user_lang(my_import.user), news=None,
                                                     version=my_import.notification_version)
        send_import_summary(my_import.user, log)
        my_import.delete()
    return HttpResponse('ok')


@backend
def import_translations_step4(request, space_id=None):
    my_import = get_object_or_404(ImportTable, pk=space_id)
    log = {'added': json.loads(my_import.added), 'conflict': json.loads(zlib.decompress(my_import.deflated_conflict)),
           'omitted': json.loads(my_import.omitted), 'not_valid': json.loads(my_import.not_valid),
           'conflict_replaced': [], 'conflict_omitted': []}
    replace_conflict = json.loads(zlib.decompress(my_import.deflated_conflict_rep))
    tl = TranslatedLang.get_or_none(lang_key = my_import.lang.lang_key)

    for rid, record in list(replace_conflict.items()):
        if record.get("checked", False):
            tl.add_label(record['name'], record['value'], overwrite=True)
            log['conflict_replaced'].append("%s = \"%s\"" % (record['name'], record['value']))
        else:
            log['conflict_omitted'].append(record['name'])

        tl.save()
    if my_import.create_notification:
        create_or_edit_translations_notification(my_import.pasted_json[1:-1], my_import.user,
                                                 get_user_lang(my_import.user), news=None,
                                                 version=my_import.notification_version)

    send_import_summary(my_import.user, log)
    my_import.delete()
    return HttpResponse('ok')

@backend
def delete_lang_async(request, lang_id, user_id):
    try:
        user = get_object_or_404(User, pk=user_id)
        lang = get_object_or_404(SupportedLanguages, pk=lang_id)
        lang_key = lang.lang_key
        tl  = TranslatedLang.get_or_none(lang_key = lang_key)
        if tl is not None:
            tl.delete()
        TranslatedImages.objects.filter(lang=lang).delete()
        delete_cached_language(lang.lang_key)
        lang.delete()
        send_delete_lang_confirmation(lang_key, user)
    except Exception:
        import traceback
        logging.exception('Language deletion failed')
        mail_admins('Language deletion failed', traceback.format_exc())
        send_delete_lang_failure(lang_key, user)
    return HttpResponse('ok')

def send_delete_lang_confirmation(lang_key, user):
    subject = get_safely_translation('lorepo.translations.views.delete_lang_confirm', get_user_lang(user), lang_key)
    context = Context({'lang_key': lang_key, 'user': user, 'app_name': APP_NAME, 'BASE_URL': settings.BASE_URL})
    email = loader.get_template('translations/delete_lang_confirmation.txt')
    rendered = email.render(context)
    send_message(SERVER_EMAIL, [user.email], subject, rendered)


def send_delete_lang_failure(lang_key, user):
    subject = get_safely_translation('lorepo.translations.views.delete_lang_fail', get_user_lang(user), lang_key)
    context = Context({'lang_key': lang_key, 'user': user, 'app_name': APP_NAME})
    email = loader.get_template('translations/delete_lang_failure.txt')
    rendered = email.render(context)
    send_message(SERVER_EMAIL, [user.email], subject, rendered)

def _update_news_info(info, news):
    year = str(news.year)
    month = str(news.month)

    if len(month) == 1:
        month = '0%s' % month

    if not info:
        info = {}
    else:
        info = json.loads(info)

    if not info.get(year, None):
        info[year] = {}

    info[year]['count'] = info[year].get('count', 0) + 1
    info[year][month] = info[year].get(month, 0) + 1

    return json.dumps(info)


def _send_notification_added_mail(news):
    translations_settings = TranslationsSettings.load()

    if not translations_settings.notification_recipients:
        return

    emails = translations_settings.notification_recipients.split(',')
    subject = news.title
    labels = json.loads("{" + news.raw_text + "}")
    body = render_to_string('translations/added_notification.txt', {
        'BASE_URL': settings.BASE_URL,
        "labels": labels,
        "news": news
    })
    send_message(settings.SERVER_EMAIL, emails, subject, body)