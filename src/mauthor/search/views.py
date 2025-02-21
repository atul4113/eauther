from django.shortcuts import render, redirect

import settings
from libraries.wiki.models import WikiPageTranslatedIndex
from lorepo.mycontent.models import Content
from mauthor.search.util import update_index, search_index, get_spaces_query, \
    parse_query, DEFAULT_SEARCH_LIMIT
from django.http import HttpResponse
from libraries.utility.decorators import backend
import logging
from django.core.mail import mail_admins
from django.utils.html import strip_tags
from mauthor.utility.db_safe_iterator import safe_iterate

MAX_UPDATE_INDEX_RETRIES = 5


@backend
def put(request, content_id):
    try:
        retries = int(request.META['HTTP_X_APPENGINE_TASKRETRYCOUNT'])
        if retries > MAX_UPDATE_INDEX_RETRIES:
            mail_admins('Update search index failed', 'Update search index failed for content %s' % content_id)
            return HttpResponse('Index not updated')
        content = Content.get_cached_or_404(id=content_id)
        update_index('lessons', content)
    except:
        import traceback
        logging.exception(traceback.format_exc())
    return HttpResponse('OK')


# Change date before start, example date: '2017-06-01 00:00:00'
@backend
def rebuild_search_from_date(request):
    try:
        for elements_batch in safe_iterate(Content.objects.filter(modified_date__gte='2017-06-01 00:00:00')):
            for element in elements_batch:
                try:
                    update_index('lessons', element)
                except:
                    import traceback
                    logging.exception(traceback.format_exc())
    except:
        import traceback
        logging.exception(traceback.format_exc())

    return HttpResponse()


def search(request):
    query_orig = strip_tags(request.GET.get('q'))
    query_parsed = parse_query(query_orig)
    referer = ''

    if 'HTTP_REFERER' in request.META:
        referer = request.META['HTTP_REFERER']
    type = request.GET.get('type', None)

    page = int(request.GET.get('page', 1))
    if page > 100:
        page = 100
    if page < 1:
        page = 1

    lang_code = settings.LANGUAGE_CODE

    if type == 'doc':
        if request.user and request.user.is_authenticated():
            lang_code = request.user.profile.language_code

        kwargs = {'language_code': lang_code, 'is_toc': True}
        query_parsed = '"%s"' % query_parsed

        result = WikiPageTranslatedIndex.search(query=query_parsed, page=page, limit=DEFAULT_SEARCH_LIMIT, **kwargs)

        return render(request, 'search/search_wiki.html',
                      {
                          'result': result,
                          'query': query_orig,
                          'page': page,
                          'lang_code': lang_code
                    })
    else:
        query = query_parsed + ' ' + get_spaces_query(request.user)
        result = search_index('lessons', query, page=page)

        return render(request, 'search/search.html', {'result' : result, 'query' : query_orig, 'page' : page})