from django import template
from django.template import defaultfilters
from src.lorepo.spaces.util import get_space_for_content
from src.lorepo.spaces.models import Space
from src.lorepo.mycontent.models import Content, ContentType
import re
import hashlib
import urllib.parse
import urllib.request, urllib.parse, urllib.error
 
register = template.Library()
 
MOMENT = 120    # duration in seconds within which the time difference 
                # will be rendered as 'a moment ago'
 
@register.filter
def naturalTimeDiff(value):
    """
    Finds the difference between the datetime value given and now()
    and returns appropriate humanize form
    """
 
    from datetime import datetime
 
    if isinstance(value, datetime):
        delta = datetime.now() - value
        if delta.days > 2*365:
            return str(delta.days/365) + ' years ago' 
        elif delta.days > 365:
            return 'year ago' 
        elif delta.days > 2*30:
            return str(delta.days/30) + ' months ago'
        elif delta.days > 30:
            return 'month ago' 
        elif delta.days > 1:
            return str(delta.days) + ' days ago' 
        elif delta.days == 1:
            return 'Yesterday' 
        elif delta.seconds > 3600:
            return str(delta.seconds / 3600 ) + ' hours ago' # 3 hours ago
        elif delta.seconds > MOMENT:
            return str(delta.seconds/60) + ' minutes ago' # 29 minutes ago
        else:
            return 'a moment ago'
                 
        return defaultfilters.date(value)
    else:
        return str(value)

@register.inclusion_tag('home/button.html')
def button(text, path, css=None, width='100%'):
    return { 'text' : text, 'path' : path, 'css' : css, 'width': width}

@register.filter
def minusOne(value):
    return value-1

@register.filter
def split(value, separator):
    return value.split(separator)

@register.filter
def request_params(params_map, additional = True):
    if not params_map:
        return ''

    params_list = []

    for key, value in list(params_map.items()):
        if key != 'type':
            params_list.append('%(key)s=%(value)s' % locals())

    starter = '&' if additional else '?'
    return starter + '&'.join(params_list)

@register.filter
def sorting_param_append(url, param):
    parsed_result = urllib.parse.urlparse(url)
    parsed_qs = urllib.parse.parse_qs(parsed_result.query)
    parsed_qs['order_by'] = [param]
    query_pairs = [(k,v) for k,vlist in list(parsed_qs.items()) for v in vlist]
    return parsed_result.path + "?" + urllib.parse.urlencode(query_pairs)

@register.inclusion_tag("simple_menu_item.html")
def simple_menu_item(request, name, path, classes, alternative_path=None):
    if request.path == path:
        classes += " selected"
    if alternative_path and re.search(alternative_path, request.path):
        classes += " selected"
    return {'name': name, 'path' : path, 'classes' : classes}

@register.simple_tag
def active(request, tab_id):
    return ''

@register.inclusion_tag("simple_menu_item.html")
def private_space_menu(request, name, path, classes):
    path_parts = request.path.split('/')
    if request.user.is_authenticated():
        space_id = None
        if re.search('^/mycontent/{0,1}$', request.path):
            classes += " selected"
        elif re.search('^/mycontent/\d+(/trash){0,1}/{0,1}$', request.path):
            space_id = path_parts[2]
            selected_space = Space.objects.get(pk=space_id)
            if selected_space.is_private():
                classes += " selected"
        elif re.search('^/mycontent/addcontent', request.path) or re.search('^/mycontent/addon', request.path):
            if len(path_parts) == 3:
                classes += " selected"
            else:
                space_id = path_parts[3]
                space = Space.objects.get(pk=space_id)
                if space.is_private():
                    classes += " selected"
        elif re.search('^/mycontent/view/\d+$', request.path):
            content_id = path_parts[3]
            try:
                content = Content.get_cached(id=content_id)
                space = get_space_for_content(content)
                if space.is_private():
                    classes += " selected"
            except (Content.DoesNotExist, Content.MultipleObjectsReturned):
                pass
        elif re.search('^/mycontent/\d+/\w+', request.path):
            content_id = path_parts[2]
            space = get_space_for_content(Content.get_cached(id=content_id))
            if space.is_private():
                classes += " selected"
            
    return {'name' : name, 'path' : path, 'classes' : classes}

@register.filter
def mod(value, arg):
    return value%arg

@register.filter
def get_range(to, from_=0):
    return list(range(from_ + 1, to + 1))

@register.simple_tag
def avatar(author):
    email = str.lower(author.email)
    email = str.strip(email)
    hash = hashlib.md5(email.encode()).hexdigest()
    return "http://www.gravatar.com/avatar/" + hash.hexdigest() + "?d=identicon"

@register.inclusion_tag("home/space_path.html")
def space_path(spaces, content_type=ContentType.LESSON):
    if content_type == ContentType.LESSON:
        content_name = "Presentations"
    elif content_type == ContentType.TEMPLATE:
        content_name = "Templates"
    elif content_type == ContentType.ADDON:
        content_name = "Addons"
    return { 'spaces' : spaces, 'content_type' : content_type, 'content_name' : content_name }