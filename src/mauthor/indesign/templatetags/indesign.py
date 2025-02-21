from django import template

register = template.Library()

@register.inclusion_tag('indesign/structure.html')
def structure(element, counter):
    return {'element' : element, 'counter' : counter}

@register.filter
def has_children(element):
    return True if list(element) else False