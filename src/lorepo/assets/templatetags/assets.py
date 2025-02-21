from django import template

register = template.Library()

@register.filter
def thumbnail_url(url, size="150,150"):
    width, height = size.split(',')
    file_path = url.split('/')
    if len(file_path) != 4:
        return ''
    file_id = file_path[3]
    return '/file/thumbnail/%(file_id)s/%(width)s/%(height)s' % locals()