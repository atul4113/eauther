import datetime
import re
from xml.dom import minidom, NotFoundErr
from xml.dom.minidom import Node

from google.appengine.ext import db
from lorepo.assets.util import create_asset_element, clean_assets
from lorepo.filestorage.models import FileStorage, UploadedFile
from lorepo.filestorage.utils import create_new_version
from lorepo.mycontent.models import Content, ContentType, ContentSpace, \
    RecentlyOpened
from lorepo.mycontent.service import get_list_by_ids
from lorepo.public.util import filter_public_contents
from lorepo.spaces.util import get_spaces_tree,\
    get_spaces_path_for_content, get_space_for_content, get_spaces_subtree
from lorepo.token.util import create_mycontent_editor_token, create_mycontent_edit_addon_token

from search.utils import partial_match_search


@db.transactional(xg=True)
def get_content_with_changed_content_file(content_id, file):
    content = Content.get_cached(id=content_id)
    content.file = file
    content.save()
    return content


def get_contents_from_space(space, space_filter=None, content_filter=None):
    contents = []
    spaces = get_spaces_tree(space.id)
    for s in spaces:
        if space_filter is not None and not space_filter(s):
            continue
        contents.extend(get_contents_from_specific_space(s.id, content_filter))

    return contents


def get_contents_from_subspaces(space, space_filter=None, content_filter=None):
    contents = []
    spaces = get_spaces_subtree(space.id)
    for s in spaces:
        if space_filter is not None and not space_filter(s):
            continue
        contents.extend(get_contents_from_specific_space(s.id, content_filter))
    return contents


def get_contents_from_specific_space(space_id, content_filter=None):
    ids = ContentSpace.objects.filter(space=space_id).values_list('content', flat=True)
    all_contents = get_list_by_ids(ids)
    if content_filter is not None:
        contents = []
        for c in all_contents:
            if not content_filter(c):
                continue
            contents.append(c)
        return contents
    else:
        return all_contents


def get_contents_from_public_space(space):
    '''Gets public contents from public space and it's subspaces.
    '''
    if not space.is_public():
        raise Exception('Space %(space)s is not public' % {'space' : space.title})
    return get_contents_from_space(space, lambda space: space.is_public(), lambda content: content.is_content_public())


def get_content_details(request, content_id, content_type=None):
    context = {}
    length = 4 if content_type == ContentType.ADDON else 5

    content = Content.get_cached_or_404(id=content_id)
    context['content'] = content
    context['public_spaces'] = get_spaces_path_for_content(content, lambda space: space.is_public())
    context['from_the_same_publisher'] = None
    search_terms = content.tags.split(',')

    from_the_same_author = content.author.content_set.filter(content_type=content_type)[:length]
    context['from_the_same_author'] = filter_public_contents(request.user, from_the_same_author)

    query_filter_args = {'content_type' : content_type }

    related_presentations = partial_match_search(Content, ' '.join(search_terms), query_filter_args)[:length]
    context['related_presentations'] = filter_public_contents(request.user, related_presentations)

    assigned_space = get_space_for_content(content)
    if assigned_space.is_corporate():
        content_filter = lambda content: content.is_content_public() and content.content_type == content_type
        context['from_the_same_publisher'] = get_contents_from_space(assigned_space, None, content_filter)[:length]

    return context


def get_addon_source_code(contents):
    doc = minidom.parseString(contents)
    source_code = {}

    view = doc.getElementsByTagName("view")[0]
    preview = doc.getElementsByTagName("preview")[0]
    presenter = doc.getElementsByTagName("presenter")[0]

    source_code["view"] = view.firstChild.nodeValue if view.firstChild is not None else ''
    source_code["preview"] = preview.firstChild.nodeValue if preview.firstChild is not None else ''
    source_code["presenter"] = presenter.firstChild.nodeValue if presenter.firstChild is not None else ''
    source_code["properties"] = ''
    for node in doc.getElementsByTagName('property'):
        source_code["properties"] += node.getAttribute('name') + ',' + node.getAttribute('type') + ',' + node.getAttribute('displayName') + ',' + node.getAttribute('isLocalized') + '\r\n'

    return source_code


def create_template_node(template_file, user):
    doc = minidom.parseString(template_file.contents)
    entry = None
    for e in doc.getElementsByTagName('entry'):
        if e.getAttribute('key') == 'theme.href':
            entry = e
            break
    if not entry:
        metadata = doc.getElementsByTagName('metadata')[0] if doc.getElementsByTagName('metadata') else None
        if not metadata:
            metadata = doc.createElement('metadata')
            ic = doc.getElementsByTagName('interactiveContent')[0]
            ic.appendChild(metadata)
        entry = doc.createElement('entry')
        entry.setAttribute('key', 'theme.href')
        metadata.appendChild(entry)
    entry.setAttribute('value', '/file/' + str(template_file.id))
    pages_tag = doc.getElementsByTagName('pages')[0] if doc.getElementsByTagName('pages') else None
    if pages_tag:
        pages = doc.getElementsByTagName('page')
        for i in range(1, pages.length): #we leave the first page (pages[0]) intact for now
            try:
                pages_tag.removeChild(pages[i]) #this will only remove immediate descendants of <pages>, it'll throw ex. for the rest (like pages under <folder name="commons">)
            except NotFoundErr:
                pass

    page_elements = doc.getElementsByTagName('page')
    for page in page_elements: #create a copy for all remaining pages
        page_file = FileStorage.objects.get(pk=page.getAttribute('href'))
        page_file = page_file.getCopy(user)
        page.setAttribute('href', str(page_file.id))
    first_page = page_elements[0]
    first_page.setAttribute('name', 'Page 1')
    contents = doc.toxml('utf-8')
    return contents


def clean_content_assets(user, content):
    urls = []
    previously_removed = False
    pattern = "([\(\"\';])(/file/serve/\d+)"
    content.modified_date = datetime.datetime.now()
    content.file = create_new_version(content.file, user, comment='assets_update', shallow=True)
    content.save()
    urls.extend(re.findall(pattern, content.file.contents))
    main_page = minidom.parseString(content.file.contents)
    assets_nodes = main_page.getElementsByTagName('assets')
    if len(assets_nodes) > 0:
        assets = assets_nodes[0]
        existing_assets = {}
        for child in assets.childNodes:
            if child.nodeType != Node.TEXT_NODE:
                existing_assets[child.getAttribute('href')] = child
    else:
        assets = None
    pages = main_page.getElementsByTagName('page')
    for page in pages:
        page_record = page.getAttribute('href')
        file_object = FileStorage.objects.get(pk=page_record)
        urls.extend(re.findall(pattern, file_object.contents))
    urls = set(urls)
    for url in urls:
        file_objects = UploadedFile.objects.filter(id=url[1].split('/')[3])
        if len(file_objects) == 0:
            continue
        file_object = file_objects[0]
        content_type = file_object.content_type
        file_type = None
        if content_type:
            file_type = content_type.split('/')[0]
        if file_type is None or file_type not in ['audio', 'image', 'video']:
            file_type = 'file'
        if url[1] in existing_assets:
            try:
                if assets:
                    assets.removeChild(existing_assets[url[1]])
                    previously_removed = False
            except NotFoundErr:
                previously_removed = True
                pass # already removed based on previous URL
        if assets:
            if (not previously_removed) or (url[1] not in existing_assets):
                new_assets = create_asset_element(main_page, url[1], file_type, file_object)
                assets.appendChild(new_assets)
    content.file.contents = main_page.toxml('utf-8')

    content.file.contents = clean_assets(content)
    content.file.save()


def get_recently_opened(user, count=5):
    return RecentlyOpened.objects.filter(user=user).order_by('-created_date')[0:count]


def save_recently_opened(user, content):
    results = RecentlyOpened.objects.filter(user=user, content=content)
    if len(results) == 0:
        recently_opened = RecentlyOpened(user=user, content=content)
    else:
        recently_opened = results[0]
    recently_opened.save()


def set_new_token_and_return_path(request):
    old_url_to_editor = request.REQUEST.get("next_url")
    where_token = old_url_to_editor.find("token")
    full_path_edit = old_url_to_editor[:where_token]

    if 'addon' in str(old_url_to_editor):
        token, token_key = create_mycontent_edit_addon_token(request.user)
        new_url_to_editor = full_path_edit + '{}={}'.format(token_key, token)

    else:
        token, token_key = create_mycontent_editor_token(request.user)
        new_url_to_editor = full_path_edit + '{}={}'.format(token_key, token)

    return new_url_to_editor
