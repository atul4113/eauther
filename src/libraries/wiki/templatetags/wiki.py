from django.template.defaultfilters import register

@register.inclusion_tag('wiki/table_of_contents.html')
def toc(wiki_pages, selected_page=None, lang_code='en'):
    return {'wiki_pages' : wiki_pages, 'selected_page' : selected_page, 'lang_code': lang_code}

@register.inclusion_tag('wiki/table_of_contents.html')
def edit_toc(wiki_pages):
    return {'wiki_pages' : wiki_pages, 'selected_page': None, 'lang_code': 'en', 'translations_edit':True}

@register.filter
def has_kids(element):
    return len(element.kids.all()) > 0
