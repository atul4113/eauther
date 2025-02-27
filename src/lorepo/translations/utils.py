from src.libraries.utility.decorators import cached

from src.libraries.utility.helpers import get_object_or_none
import src.libraries.utility.cacheproxy as cache
from src.lorepo.translations.models import SupportedLanguages, TranslatedImages, TranslatedLang
from src.lorepo.user.models import UserProfile
from src.settings import USER_DEFAULT_LANG
from django.contrib import messages

TRANSLATION_CACHE_TIMEOUT = 60 * 60 * 24 * 7


def get_static_language(lang_key):
    language_id = cache.get("Lang:%s" % (lang_key))
    if language_id == None:
        language = get_object_or_none(SupportedLanguages,lang_key = lang_key)
        if language == None:
            language_id = None
        else:
            language_id = language.id
            cache.set("Lang:%s" % (lang_key), language_id, TRANSLATION_CACHE_TIMEOUT)
    return language_id


def delete_cached_language(lang_key):
    cache.delete("Lang:%s" % (lang_key))

@cached(timeout=TRANSLATION_CACHE_TIMEOUT, params_key=lambda l: str(l.id))
def get_translated_images(lang):
    translations = TranslatedImages.objects.filter(lang = lang)
    trans_dict = {}
    for t in translations:
        trans_dict[t.label] = "/file/serve/%s" % t.file_id
    return trans_dict


def get_translation(label, lang):
    tl = TranslatedLang.get_or_none(lang_key=lang)
    if tl is None:
        return '{{%s} Lanuage %s is not specified.}' % (label, lang)
    try:
        return tl.get_translation(label)
    except KeyError:
        return '{{%s} not set in lang %s}' % (label, lang)
    return value


def get_safely_translation_utf8(label, lang, params=None):
    return get_safely_translation(label, lang, params).encode('utf-8')


def get_safely_translation(label, lang, params=None):
    label_value = get_translation(label, lang)
    if params == None:
        return label_value
    if type(params) == tuple or type(params) == list:
        number_of_params = len(params)
        number_of_dynamics = label_value.count('%s')
        if number_of_dynamics == number_of_params:
            return label_value % params
        else:
            return label_value
    elif type(params) == str or type(params) == str:
        if label_value.count('%s'):
            return label_value % params
        else:
            return label_value
    elif type(params) == dict:
        all_ok = True
        import re
        pattern = r'(%\(\w+\)s)'
        compare_s = re.findall(pattern, label_value)
        if compare_s:
            for s in compare_s:
                s = s.replace('%(','').replace(')s','')
                if not (s in params):
                    all_ok = False
        else:
            all_ok = False
        if all_ok:
            return label_value % params
        else:
            return label_value
    else:
        return label_value



def save_translation_instance(trans):
    cache.delete("Trans:%s.%s" % (trans.lang.lang_key, trans.name))
    return trans.save()


def save_translated_image_to_cache(label, lang, image):
    cache.set("Trans_img:%s.%s" % (lang, label), image.id, TRANSLATION_CACHE_TIMEOUT)


def delete_cache_translated_image(img):
    cache.delete("Trans_img:%s.%s" % (img.lang.lang_key, img.label))


def get_translated_image(label, lang, def_value=None):
    value = cache.get("Trans_img:%s.%s" % (lang,label))
    if value == None:
        language = get_static_language(lang)
        if language == None:
            value = -2 # not specified language
        else:
            record = get_object_or_none(TranslatedImages, lang = language, label = label)
            if record == None:
                value = -1 # not specified label
            else:
                value = record.file.id
        cache.set("Trans_img:%s.%s" % (lang, label), value, TRANSLATION_CACHE_TIMEOUT)
    if value > 0:
        return '/file/serve/' + str(value)
    elif def_value:
        return def_value
    else:
        return '/media/img/no-image.png'


def change_session_lang(request, lang=None):
    if lang == None:
        if 'userlang' in request.POST:
            if request.user.is_authenticated():
                profile = UserProfile.get_for_user(user=request.user)
                profile.lang = SupportedLanguages.objects.get(lang_key=request.POST['userlang'])
                profile.save()
            request.session['USER_LANG']=request.POST['userlang']
    else:
        if get_object_or_none(SupportedLanguages, lang_key=lang):
            request.session['USER_LANG'] = lang


def get_request_lang(request):
    if hasattr(request,'session'):
        if 'USER_LANG' in request.session:
            return request.session['USER_LANG']
    return USER_DEFAULT_LANG


def get_user_lang(user):
    user_profile = user.profile
    user_lang = USER_DEFAULT_LANG
    if user_profile != None:
        if user_profile.lang:
            user_lang = user_profile.lang.lang_key
    return user_lang       


def get_sys_label(request, value, params=None):
    return get_safely_translation(value, get_request_lang(request), params).encode('utf-8')


def message_from_label(type, request, label, params=None):
    msg = getattr(messages, type)
    return msg(request, get_safely_translation(label, get_request_lang(request), params))


def get_mst_labels(request, labels):
    mst_labels = {}
    for label in labels:
        mst_labels[label.replace('.','_')] = get_sys_label(request, label)
    return mst_labels


class TranslateFormMixin(object):

    def get_form(self):
        form = super(TranslateFormMixin, self).get_form()
        for field_name in self.translate_fields:
            label_name = self.translate_prefix + field_name
            form.fields[field_name].label = get_sys_label(self.request, label_name)
        return form


class TranslatedException(Exception):
    label = 'lorepo.undefined'
    params = None

    def __init__(self, label, params=None, *args, **kwargs):
        self.label = label
        self.params = params
        return super(TranslatedException, self).__init__(*args, **kwargs)

    def add_message(self, request):
        message_from_label('error', request, self.label, self.params)

    def get_text(self, request):
        return get_sys_label(request, self.label, self.params)