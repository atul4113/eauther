from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django.db import transaction
from xml.dom import minidom, NotFoundErr
import xml.etree.ElementTree as ET
import re
import datetime
from lorepo.spaces.util import get_spaces_tree, get_spaces_path_for_content, get_space_for_content, get_spaces_subtree
from lorepo.mycontent.models import Content, ContentType, ContentSpace, UpdateTemplateStatus, RecentlyOpened
from lorepo.filestorage.models import FileStorage, UploadedFile
from lorepo.filestorage.utils import create_new_version
from lorepo.assets.util import create_asset_element, clean_assets
from lorepo.public.util import filter_public_contents
from search.utils import partial_match_search
from lorepo.mycontent.service import get_list_by_ids

@transaction.atomic
def get_content_with_changed_content_file(content_id, file):
    """
    Updates the content's file and saves it.
    """
    content = get_object_or_404(Content, id=content_id)
    content.file = file
    content.save()
    return content

def get_contents_from_space(space, space_filter=None, content_filter=None):
    """
    Retrieves contents from a space and its subspaces, optionally filtered.
    """
    contents = []
    spaces = get_spaces_tree(space.id)
    for s in spaces:
        if space_filter is not None and not space_filter(s):
            continue
        contents.extend(get_contents_from_specific_space(s.id, content_filter))
    return contents

def get_contents_from_subspaces(space, space_filter=None, content_filter=None):
    """
    Retrieves contents from subspaces of a given space, optionally filtered.
    """
    contents = []
    spaces = get_spaces_subtree(space.id)
    for s in spaces:
        if space_filter is not None and not space_filter(s):
            continue
        contents.extend(get_contents_from_specific_space(s.id, content_filter))
    return contents

def get_contents_from_specific_space(space_id, content_filter=None):
    """
    Retrieves contents from a specific space, optionally filtered.
    """
    ids = ContentSpace.objects.filter(space__id=space_id).values_list('content', flat=True)
    all_contents = get_list_by_ids(ids)
    if content_filter is not None:
        return [c for c in all_contents if content_filter(c)]
    return all_contents

def get_contents_from_public_space(space):
    """
    Retrieves public contents from a public space and its subspaces.
    """
    if not space.is_public():
        raise Exception(f'Space {space.title} is not public')
    return get_contents_from_space(space, lambda s: s.is_public(), lambda c: c.is_content_public())

def get_content_details(request, content_id, content_type=None):
    """
    Retrieves detailed information about a content item.
    """
    context = {}
    length = 4 if content_type == ContentType.ADDON else 5

    content = get_object_or_404(Content, id=content_id)
    context['content'] = content
    context['public_spaces'] = get_spaces_path_for_content(content, lambda s: s.is_public())
    context['from_the_same_publisher'] = None
    search_terms = content.tags.split(',')

    from_the_same_author = content.author.content_set.filter(content_type=content_type)[:length]
    context['from_the_same_author'] = filter_public_contents(request.user, from_the_same_author)

    query_filter_args = {'content_type': content_type}
    related_presentations = partial_match_search(Content, ' '.join(search_terms), query_filter_args)[:length]
    context['related_presentations'] = filter_public_contents(request.user, related_presentations)

    assigned_space = get_space_for_content(content)
    if assigned_space.is_corporate():
        context['from_the_same_publisher'] = get_contents_from_space(assigned_space, None, lambda c: c.is_content_public() and c.content_type == content_type)[:length]

    return context

def get_addon_source_code(contents):
    """
    Extracts source code from an addon's XML content.
    """
    doc = minidom.parseString(contents)
    source_code = {
        "view": doc.getElementsByTagName("view")[0].firstChild.nodeValue if doc.getElementsByTagName("view")[0].firstChild else '',
        "preview": doc.getElementsByTagName("preview")[0].firstChild.nodeValue if doc.getElementsByTagName("preview")[0].firstChild else '',
        "presenter": doc.getElementsByTagName("presenter")[0].firstChild.nodeValue if doc.getElementsByTagName("presenter")[0].firstChild else '',
        "properties": ''
    }
    for node in doc.getElementsByTagName('property'):
        source_code["properties"] += f"{node.getAttribute('name')},{node.getAttribute('type')},{node.getAttribute('displayName')},{node.getAttribute('isLocalized')}\r\n"
    return source_code

def create_template_node(template_file, user):
    """
    Creates a template node from a template file.
    """
    doc = minidom.parseString(template_file.contents)
    entry = None
    for e in doc.getElementsByTagName('entry'):
        if e.getAttribute('key') == 'theme.href':
            entry = e
            break
    if not entry:
        metadata = doc.getElementsByTagName('metadata')[0] if doc.getElementsByTagName('metadata') else doc.createElement('metadata')
        ic = doc.getElementsByTagName('interactiveContent')[0]
        ic.appendChild(metadata)
        entry = doc.createElement('entry')
        entry.setAttribute('key', 'theme.href')
        metadata.appendChild(entry)
    entry.setAttribute('value', f'/file/{template_file.id}')
    pages_tag = doc.getElementsByTagName('pages')[0] if doc.getElementsByTagName('pages') else None
    if pages_tag:
        pages = doc.getElementsByTagName('page')
        for i in range(1, len(pages)):
            try:
                pages_tag.removeChild(pages[i])
            except NotFoundErr:
                pass

    page_elements = doc.getElementsByTagName('page')
    for page in page_elements:
        page_file = FileStorage.objects.get(pk=page.getAttribute('href'))
        page_file = page_file.getCopy(user)
        page.setAttribute('href', str(page_file.id))
    first_page = page_elements[0]
    first_page.setAttribute('name', 'Page 1')
    return doc.toxml('utf-8')

def get_company_templates(company):
    """
    Retrieves templates associated with a company.
    """
    return Content.objects.filter(content_type=ContentType.TEMPLATE, is_deleted=False, spaces=str(company.id))

def update_content_template(content, user, preferences, template_content=None):
    """
    Updates a content item with a new template.
    """
    if content.who_is_editing() is not None:
        return UpdateTemplateStatus.CONTENT_CURRENTLY_EDITED

    comment = 'template_change'
    if not template_content:
        template_content = content.get_template()
        comment = 'template_update'
    if not template_content:
        return UpdateTemplateStatus.NO_TEMPLATE
    if template_content.who_is_editing() is not None:
        return UpdateTemplateStatus.TEMPLATE_CURRENTLY_EDITED

    newest_template_file = FileStorage.objects.filter(history_for__id=template_content.id).order_by('-version').first()
    template_contents = ET.fromstring(newest_template_file.contents)
    styles = template_contents.findall('style')
    content.file = create_new_version(content.file, user, comment=comment, shallow=True)
    content.save()
    page = minidom.parseString(content.file.contents)
    new_style = None
    no_template_in_lesson = True

    for entry in page.getElementsByTagName('entry'):
        if entry.getAttribute('key') == 'theme.href':
            no_template_in_lesson = False
            entry.setAttribute('value', f'/file/{newest_template_file.pk}')
            break

    if no_template_in_lesson:
        metadata = page.getElementsByTagName('metadata')[0] if page.getElementsByTagName('metadata') else page.createElement('metadata')
        ic = page.getElementsByTagName('interactiveContent')[0]
        ic.appendChild(metadata)
        entry = page.createElement('entry')
        entry.setAttribute('key', 'theme.href')
        metadata.appendChild(entry)
        entry.setAttribute('value', f'/file/{newest_template_file.id}')

    update_addon_descriptors(page, template_contents.findall('addons')[0])
    content.file.contents = page.toxml(encoding='utf-8')
    cache.set(f"content_template_{content.id}", template_content, 60 * 60 * 24)

    if styles:
        new_style = styles[0]
        styles_in_page = page.getElementsByTagName('style')
        if styles_in_page:
            if styles_in_page[0].firstChild:
                styles_in_page[0].firstChild.nodeValue = new_style.text
            else:
                style_value = page.createTextNode(new_style.text)
                styles_in_page[0].appendChild(style_value)
        else:
            style = page.createElement('style')
            ic = page.getElementsByTagName('interactiveContent')[0]
            ic.appendChild(style)
            style_value = page.createTextNode(new_style.text)
            style.appendChild(style_value)
        content.file.contents = page.toxml(encoding='utf-8')

    propagate_preferences(preferences, page, newest_template_file)
    content.file.contents = page.toxml(encoding='utf-8')
    content.file.save()

    return UpdateTemplateStatus.UPDATED

def propagate_preferences(preferences, page, template_content_file):
    """
    Propagates template preferences to the content.
    """
    if preferences:
        metadata = page.getElementsByTagName('metadata')[0] if page.getElementsByTagName('metadata') else page.createElement('metadata')
        ic = page.getElementsByTagName('interactiveContent')[0]
        ic.appendChild(metadata)
        entries = metadata.getElementsByTagName('entry')

        template = minidom.parseString(template_content_file.contents)
        template_entries = template.getElementsByTagName('entry')

        for preference in ['use_grid', 'grid_size', 'static_header', 'static_footer']:
            if preference in preferences:
                add_preference_entry(template_entries, entries, preference.replace('_', '').capitalize(), metadata)

def add_preference_entry(template_entries, entries, preference_name, metadata):
    """
    Adds a preference entry to the metadata.
    """
    template_preference_value = None
    for template_entry in template_entries:
        if template_entry.getAttribute('key') == preference_name:
            template_preference_value = template_entry.getAttribute('value')

    if template_preference_value is not None:
        if is_preference_in_entry(entries, preference_name):
            for entry in entries:
                if entry.getAttribute('key') == preference_name:
                    entry.setAttribute('value', template_preference_value)
        else:
            entry = metadata.ownerDocument.createElement('entry')
            entry.setAttribute('key', preference_name)
            metadata.appendChild(entry)
            entry.setAttribute('value', template_preference_value)

def is_preference_in_entry(entries, preference_name):
    """
    Checks if a preference is already in the entries.
    """
    return any(entry.getAttribute('key') == preference_name for entry in entries)

def update_addon_descriptors(page, new_addons_node):
    """
    Updates addon descriptors in the content.
    """
    existing_descriptors = page.getElementsByTagName('addon-descriptor')
    existing_ids = [desc.getAttribute('addonId') for desc in existing_descriptors]

    descriptors = {}
    for descriptor in new_addons_node.findall('addon-descriptor'):
        if descriptor.attrib['addonId'] not in existing_ids:
            descriptors[descriptor.attrib['addonId']] = descriptor.attrib['href']

    addons = page.getElementsByTagName('addons')
    addons_node = addons[0] if addons else page.createElement('addons')
    ic = page.getElementsByTagName('interactiveContent')[0]
    ic.appendChild(addons_node)

    for addon_id, href in descriptors.items():
        addon_descriptor = page.createElement('addon-descriptor')
        addon_descriptor.setAttribute('addonId', addon_id)
        addon_descriptor.setAttribute('href', href)
        addons_node.appendChild(addon_descriptor)

def clean_content_assets(user, content):
    """
    Cleans up unused assets in the content.
    """
    urls = []
    previously_removed = False
    pattern = r"([\(\"\';])(/file/serve/\d+)"
    content.modified_date = datetime.datetime.now()
    content.file = create_new_version(content.file, user, comment='assets_update', shallow=True)
    content.save()
    urls.extend(re.findall(pattern, content.file.contents))
    main_page = minidom.parseString(content.file.contents)
    assets_nodes = main_page.getElementsByTagName('assets')
    existing_assets = {}
    if assets_nodes:
        assets = assets_nodes[0]
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
        if not file_objects:
            continue
        file_object = file_objects[0]
        content_type = file_object.content_type
        file_type = content_type.split('/')[0] if content_type else 'file'
        if file_type not in ['audio', 'image', 'video']:
            file_type = 'file'
        if url[1] in existing_assets:
            try:
                if assets:
                    assets.removeChild(existing_assets[url[1]])
                    previously_removed = False
            except NotFoundErr:
                previously_removed = True
        if assets and (not previously_removed or url[1] not in existing_assets):
            new_assets = create_asset_element(main_page, url[1], file_type, file_object)
            assets.appendChild(new_assets)

    content.file.contents = main_page.toxml('utf-8')
    content.file.save()
    clean_assets(content)

def get_recently_opened(user, count=5):
    """
    Retrieves recently opened content for a user.
    """
    return RecentlyOpened.objects.filter(user=user).order_by('-created_date')[:count]

def save_recently_opened(user, content):
    """
    Saves a recently opened content item for a user.
    """
    recently_opened, created = RecentlyOpened.objects.get_or_create(user=user, content=content)
    recently_opened.save()

from django.urls import reverse

def get_redirect_url(request):
    """
    Returns the redirect URL based on request data or defaults to the home page.
    """
    # Example: if a 'next' parameter exists in the query params, return that, otherwise return the home page.
    return request.GET.get('next', reverse('home'))  # Adjust 'home' with your actual home URL name

def set_new_token_and_return_path(request):
    """
    Sets a new token and returns the full path to the editor.
    This is a placeholder, adjust according to your token logic.
    """
    # Example of token setting logic, assuming JWT or some token-based approach
    # This is just a mock implementation for demonstration purposes.
    token = "new_token"  # Replace with actual logic to generate a token
    return f"/editor/?token={token}"
