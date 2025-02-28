import json
import xml.dom.minidom
import re
from src.lorepo.filestorage.models import UploadedFile, FileStorage
from src.lorepo.assets.models import LessonCleaner
from django.template import loader, Context
from src.lorepo.public.util import send_message
from src import settings


def update_content_assets(content, uploaded_files):
    doc = xml.dom.minidom.parseString(content.file.contents)
    assets = doc.getElementsByTagName('assets')
    if len(assets) == 0:
        assets = doc.createElement('assets')
        root = doc.getElementsByTagName('interactiveContent')[0]
        root.appendChild(assets)
    else:
        assets = assets[0]
    if not type(uploaded_files) is list:
        uploaded_files = [uploaded_files]
    for uploaded_file in uploaded_files:
        if uploaded_file.content_type:
            type_index = 1 if 'svg+xml' in uploaded_file.content_type else 0
            content_type = uploaded_file.content_type.split('/')[type_index]
        else:
            content_type = 'application/octet-stream'
        new_asset = create_asset_element(doc, '/file/serve/%(id)s' % {'id' : uploaded_file.id},
                                     content_type,
                                     uploaded_file)

        assets.appendChild(new_asset)
    content.file.contents = doc.toxml('utf-8')
    content.file.save()


def update_asset_title(content, href, title):
    doc = xml.dom.minidom.parseString(content.file.contents)
    assets = doc.getElementsByTagName('asset')
    for asset in assets:
        if asset.getAttribute('href') == href:
            asset.setAttribute('title', title)
            file_id = href.split('/')[3]
            file_obj = UploadedFile.objects.get(pk=file_id)
            file_obj.title = title
            file_obj.save()
            break
    content.file.contents = doc.toxml('utf-8')
    content.file.save()


def delete_asset(content, href):
    doc = xml.dom.minidom.parseString(content.file.contents)
    assets = doc.getElementsByTagName('asset')
    for asset in assets:
        if asset.getAttribute('href') == href:
            break
    assets_node = doc.getElementsByTagName('assets')[0]
    assets_node.removeChild(asset)
    content.file.contents = doc.toxml('utf-8')
    content.file.save()


def create_asset_element(doc, href, type, file_obj):
    new_asset = doc.createElement('asset')
    new_asset.setAttribute('href', href if href else '')
    new_asset.setAttribute('type', type if type else '')
    new_asset.setAttribute('title', file_obj.title if file_obj.title else '')
    new_asset.setAttribute('fileName', file_obj.filename if file_obj.filename else '')
    new_asset.setAttribute('contentType', file_obj.content_type if file_obj.content_type else '')
    return new_asset


def clean_assets(content):
    file_serves = []
    addons_in_lesson_list = []

    cleaner = LessonCleaner(content.file)
    pages_ids = cleaner.get_attribute_values_from_many_nodes('href', cleaner.get_pages_nodes())
    assets_hrefs = cleaner.get_attribute_values_from_many_nodes('href', cleaner.get_assets_nodes())
    descriptors = cleaner.get_descriptors_nodes()

    for page_id in pages_ids:
        page = FileStorage.objects.get(pk = page_id)
        file_serves.extend(cleaner.get_all_file_serves_from_page(page))
        addons_in_lesson_list.extend(cleaner.get_all_addons_from_page(page))

    addons_in_lesson_set = set(addons_in_lesson_list)
    file_serves.extend(cleaner.get_all_file_serves_from_styles())
    non_used = cleaner.get_non_used_assets_nodes(assets_hrefs, file_serves)
    found_nodes = cleaner.get_node('assets')

    unused_descriptors = [descriptor for descriptor in descriptors if descriptor.hasAttribute("addonId") and descriptor.getAttribute("addonId") not in addons_in_lesson_set]

    if found_nodes is not None:
        cleaner.delete_specific_nodes(found_nodes, non_used)

    if len(unused_descriptors) > 0:
        cleaner.delete_unused_descriptors(unused_descriptors)

    return cleaner.print_doc()


def _validate_assets_replacement_data(assets_data):
    try:
        assets_json = json.loads(assets_data)

        if len(assets_json) == 0:
            return {'is_valid': False, 'message': 'Empty assets configuration'}

        for old_asset, new_asset in list(assets_json.items()):
            if not old_asset or not new_asset:
                return {'is_valid': False, 'message': 'Invalid asset configuration: %s -> %s' % (old_asset, new_asset)}

            pattern = re.compile("/file/serve/[0-9]+")
            old_match = re.match(pattern, old_asset)
            new_match = re.match(pattern, new_asset)

            if old_match is None or new_match is None:
                return {'is_valid': False, 'message': 'Assets does not match pattern: %s -> %s' % (old_asset, new_asset)}
    except Exception:
        return {'is_valid': False, 'message': 'Invalid syntax'}

    return {'is_valid': True}


def _replace_assets_in_lesson(lesson, assets):
    lesson_status = False
    main_xml = xml.dom.minidom.parseString(lesson.file.contents)
    status = _replace_assets_in_lesson_page(lesson.file, assets)
    lesson_status = lesson_status or status

    for node in main_xml.getElementsByTagName('page'):
        href = re.findall('\d+', node.getAttribute('href'))[0]
        page = FileStorage.objects.get(pk=href)

        status = _replace_assets_in_lesson_page(page, assets)
        lesson_status = lesson_status or status

    return lesson_status


def _replace_assets_in_lesson_page(page, assets):
    contents = page.contents
    replaced_any_asset = False

    for asset in list(assets.keys()):
        replacement_result = _replace_asset_in_page(contents, asset, assets[asset])
        replaced_any_asset = replaced_any_asset or replacement_result['status']
        contents = replacement_result['contents']

    if replaced_any_asset:
        page.contents = contents
        page.save()

    return replaced_any_asset


def _replace_asset_in_page(contents, asset, replacement):
    status = False
    pattern = re.compile("%s[^\d]" % asset)

    while True:
        # Regex finditer() gives us all occurrences of specified pattern. If we change the string, we need to find
        # this occurrences again (and again, and again...) as long as there are no left. If we would just replace
        # strings according to positions returned by function - second and later replacements would take place at
        # wrong positions and XML would be invalid.
        matches = re.finditer(pattern, contents)
        try:
            match = next(matches)
            status = True
            # Regex match position tells us where the match ends but it points to next character that doesn't match
            # our pattern. When replacing old string with new one we need to remember it and replace 1 character less.
            contents = contents[:match.start()] + replacement.encode("utf-8") + contents[match.end() - 1:]
        except StopIteration:
            break

    return {'status': status, 'contents': contents}


def replace_content_page_names(contents, main_xml, prefix):
    # prefix is escaped by the library
    replaced_any_name = False
    title_counter = 0
    for node in main_xml.getElementsByTagName('page'):
        parent = node.parentNode
        parent_name = parent.getAttribute('name')
        if parent_name != 'commons':
            title_counter += 1
            title = prefix + str(title_counter)
            node.setAttribute('name', title)
            contents = main_xml.toxml('utf-8')
            replaced_any_name = True

    return replaced_any_name, contents


def _send_replacement_status_info(config, log, subject_text, template):
    subject = subject_text
    context = Context({'config': config, 'log': log, 'settings': settings})
    email = loader.get_template(template).render(context)
    send_message(settings.SERVER_EMAIL, [config.user.email], subject, email)
