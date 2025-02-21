import google.appengine.api.search as search
import re

from mauthor.metadata.util import get_metadata_values, get_page_metadata
from lorepo.spaces.models import SpaceAccess
from lorepo.spaces.util import get_space_for_content

DEFAULT_SEARCH_LIMIT = 10

def update_index(index_name, content):
    index = search.Index(index_name)
    if content.is_deleted:
        document = index.get(str(content.id))
        if document is not None:
            index.delete(str(content.id))
    else:
        space_type = get_space_for_content(content).space_type
        document = search.Document(doc_id=str(content.id),
                               fields=[search.TextField(name='title', value=content.title.lower()),
                                       search.TextField(name='tags', value=content.tags.lower()),
                                       search.TextField(name='short_description', value=content.short_description.lower()),
                                       search.TextField(name='description', value=content.description.lower()),
                                       search.TextField(name='spaces', value=',%s,' % content.spaces_path),
                                       search.AtomField(name='author', value=str(content.author.id)),
                                       search.TextField(name='icon_href', value='%s' % content.icon_href),
                                       search.NumberField(name='space_type', value=int(space_type)),
                                       search.TextField(name='assigned_space', value=content.spaces[-1])
                                       ])
        custom_metadata = get_metadata_values(content)
        value = ''
        for metadata in custom_metadata:
            value = value + ' ' + metadata.entered_value
        document.fields.append(search.TextField(name='custom_metadata', value=value.lower()))
        
        page_metadata = get_page_metadata(content)
        value = ''
        for page in page_metadata:
            value = value + ' ' + page.title
            value = value + ' ' + page.tags
            value = value + ' ' + page.description
            value = value + ' ' + page.short_description
            for extended in page.metadata_values:
                value = value + ' ' + extended.entered_value
        document.fields.append(search.TextField(name='page_metadata', value=value.lower()))
        
        index.put(document)

def search_index(index_name, query, page=1, limit=DEFAULT_SEARCH_LIMIT):
    index = search.Index(index_name)
    sort_opts = search.SortOptions(match_scorer=search.MatchScorer())
    options = search.QueryOptions(sort_options=sort_opts, limit=limit, offset=(page-1)*limit)
    query = search.Query(query, options=options)
    return index.search(query=query)

def get_spaces_query(user):
    ids = SpaceAccess.objects.filter(user__id=user.id).values_list('space', flat=True)
    query = ' OR '.join(['\,%s\,' % id for id in ids])
    return 'spaces:(%s)' % query

def parse_query(query):
    '''
    Clears query from unsupported operations
    '''

    query = query.replace('\\', ' ')

    tokenizing_chars = ['!', '"', '%', '(', ')', '*', ',', '|', '/', '[',
                        ']', '^', '`', ':', '=', '>', '<', '?', '@', '{',
                        '}', '~', '$']

    for char in tokenizing_chars:
        query = query.replace(char, ' ')

    # - + preceded by whitespace needs to be removed
    query = re.sub(r'(\s|^)([-+]+)', ' ', query)

    # - followed by whitespace needs to be removed
    query = re.sub(r'([-]+)(\s|$)', ' ', query)

    return query