from django.template.defaultfilters import register
from django.utils.html import escapejs
from lorepo.translations.models import TranslatedLang
from lorepo.translations.utils import get_translated_image, get_safely_translation
from settings import USER_DEFAULT_LANG
from libraries.utility.helpers import get_object_or_none
from lorepo.user.models import UserProfile
from lorepo.translations.images import images_labels


@register.simple_tag(takes_context=True)
def get_label(context, value, params=None):
    # params -> str / unicode / dict / list / tuple
    if 'request' in context and context['request'] is not None:
        if not ('USER_LANG' in context['request'].session):
            context['request'].session['USER_LANG'] = USER_DEFAULT_LANG
        return get_safely_translation(value, context['request'].session['USER_LANG'], params)
    elif 'user' in context:
        profile = get_object_or_none(UserProfile, user=context['user'])
        if profile != None:
            if profile.lang:
                return get_safely_translation(value, profile.lang.lang_key, params)
    return get_safely_translation(value, USER_DEFAULT_LANG, params)


@register.simple_tag(takes_context=True)
def get_django_label(context, value):
    if value.find('Ensure this value has at most') >= 0:
        import re

        re_max = re.search('most ([0-9]+) characters \(it has ([0-9]+)\)', value)
        if re_max:
            my_dict = {'max': re_max.group(1), 'ithas': re_max.group(2)}
            return get_label(context, 'django.Ensure_this_value_has_at_most') % my_dict
        else:
            return get_label(context, 'django.Ensure_this_value_has_the_correct_number_of_characters')
    elif value.find('Select a valid choice') == 0:
        import re

        re_max = re.search('Select a valid choice. (\w+) is not one of the available choices', value)
        if re_max:
            return get_label(context, 'django.Select_a_valid_choice') % re_max.group(1)
    elif value.find('Lorepo.') == 0 or value.find('lorepo.') == 0:
        return get_label(context, 'l' + value[1:])
    value = 'django.' + TranslatedLang.make_label(value)

    return get_label(context, value)


@register.simple_tag(takes_context=True)
def get_js_label(context, label):
    value = get_label(context, label)
    value = escapejs(value)
    return value


@register.simple_tag(takes_context=True)
def get_country_label(context, value, defvalue):
    label = 'django.countries.%s' % value
    label_value = get_label(context, label)
    if label_value.find('{{') >= 0 and label_value.find(label) >= 0:
        return defvalue
    else:
        return label_value


@register.filter
def filter_label_usage(value):
    if value[0:7] == 'lorepo.':
        return filter_sys_label_usage(value)
    else:
        return filter_template_label_usage(value)


def filter_sys_label_usage(value):
    return "get_sys_label(request, '" + value + "')"


def filter_template_label_usage(value):
    return "{% get_label '" + value + "' %}"


@register.inclusion_tag('translations/filter_label_space.html')
def filter_label_space(namespace, lang):
    my_array = namespace.split(".")
    if lang != None:
        elements = '/translations/dev/_' + lang + '/'
    else:
        elements = '/translations/dev/'
    urls = []
    for i, k in enumerate(my_array):
        if i == len(my_array) - 1:
            elements += k
        else:
            elements += k + '.'
            k += '.'
        urls.append((elements, k))
    return {'urls': urls}


@register.simple_tag(takes_context=True)
def get_image_label(context, value, def_value=None):
    if 'request' in context:
        if not ('USER_LANG' in context['request'].session):
            context['request'].session['USER_LANG'] = USER_DEFAULT_LANG
        return get_translated_image(value, context['request'].session['USER_LANG'], def_value)
    elif 'user' in context:
        profile = get_object_or_none(UserProfile, user=context['user'])
        if profile != None:
            if profile.lang:
                return get_translated_image(value, profile.lang.lang_key, def_value)
    return get_translated_image(value, USER_DEFAULT_LANG, def_value)


@register.filter
def filter_image_label_usage(value):
    return "{% get_image_label '" + value + "' %}"


@register.filter
def image_placement(label):
    for entry in images_labels:
        if entry[0] == label:
            return entry[1]
    return label


AVAILABLE_DATE_PICKER_LANGS = ['en_US', 'fr-FR', 'PL', 'MX']


@register.simple_tag(takes_context=True)
def get_datepicker_localization_file(context):
    lang_key = USER_DEFAULT_LANG

    if 'request' in context:
        if 'USER_LANG' in context['request'].session:
            lang_key = context['request'].session['USER_LANG']
    elif 'user' in context:
        profile = get_object_or_none(UserProfile, user=context['user'])
        if profile is not None and profile.lang:
            lang_key = profile.lang.lang_key

    if lang_key not in AVAILABLE_DATE_PICKER_LANGS:
        lang_key = 'en_US'

    return '/media/js/jquery_datepicker/datepicker-%s.js' % lang_key