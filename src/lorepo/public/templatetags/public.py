from django.template.defaultfilters import register
from lorepo.spaces.util import get_space_for_content, get_space_type

@register.inclusion_tag('public/tags/contents_thumbnail.html')
def content_thumbnails(request, contents, ul_class=None):
    return {'request' : request, 'contents' : contents, 'ul_class' : ul_class}

@register.inclusion_tag('public/tags/space_for_content.html')
def get_space_link_for_content(content):
    space = get_space_for_content(content)
    space_type = 'mycontent' if space.is_private() else 'corporate/list'
    return { 'space' : space, 'type' : space_type }

@register.inclusion_tag('public/tags/content_link.html')
def get_content_link(content):
    content.space_type = get_space_type(content)
    return { 'content' : content }