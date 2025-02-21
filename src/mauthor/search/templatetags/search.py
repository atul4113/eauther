from django.template.defaultfilters import register
from mauthor.search.util import DEFAULT_SEARCH_LIMIT

@register.filter
def get_field(result, name):
    for field in result.fields:
        if field.name == name:
            return field.value
    return None

@register.filter
def get_id(result):
    return result.doc_id


@register.inclusion_tag('search/paginator.html')
def search_paginator(page, total, query):
    total_pages = total / DEFAULT_SEARCH_LIMIT + 1
    begining = page - 5 if page > 6 else 1
    end = page + 4 if page + 4 < total_pages else total_pages
    page_range = list(range(begining, end + 1))
    return {'page' : page, 'total_pages' : total_pages, 'page_range' : page_range, 'query' : query}


@register.inclusion_tag('search/paginator_doc.html')
def search_paginator_doc(page, total, query):
    total_pages = total / DEFAULT_SEARCH_LIMIT + 1
    begining = page - 5 if page > 6 else 1
    end = page + 4 if page + 4 < total_pages else total_pages
    page_range = list(range(begining, end + 1))
    return {'page' : page, 'total_pages' : total_pages, 'page_range' : page_range, 'query' : query}


@register.filter
def smart_truncate(content, length=235, suffix=' (...)'):
    if len(content) <= length:
        return content
    else:
        return ' '.join(content[:length+1].split(' ')[0:-1]) + suffix