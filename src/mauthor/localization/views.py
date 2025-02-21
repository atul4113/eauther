from lorepo.mycontent.decorators import IsBeingEdited
from mauthor.localization.models import Xliff, ContentXML, Field, Module,\
    Comparer
from django.shortcuts import get_object_or_404, render
from libraries.utility.queues import trigger_backend_task
from django.contrib import messages
import logging
from django.contrib.auth.models import User
from django.core.mail import mail_admins
from django.http import HttpResponse, HttpResponseRedirect
from mauthor.localization.utils import create_upload_file, get_xliff, get_upload_form,\
    get_upload_url, get_uploaded_file, make_copy_and_put_into_space,\
    get_uploaded_xliff, get_space, get_content, create_id_string
from libraries.utility.redirect import get_redirect, get_redirect_url
from mauthor.localization.exceptions import NoModulesFoundException, NodeNotFoundException, ContentException,\
    ContentTooBigException
import xml.parsers.expat
from lorepo.mycontent.models import Content
from lorepo.filestorage.utils import create_xliff_filestorage, create_new_version
from xml.dom import minidom
import datetime
from lorepo.filestorage.models import FileStorage
from django.contrib.auth.decorators import login_required
from django.conf.global_settings import LANGUAGES
from libraries.utility.environment import get_versioned_module
from mauthor.localization.notifications import send_export_success_notification,\
    send_export_failure_notification, send_import_success_notification,\
    send_import_failure_notification, send_create_xliff_success_notification,\
    send_create_xliff_failure_notification, send_content_too_big_notification
from libraries.utility.decorators import backend

@login_required
def create_export(request, content_id):
    if request.POST:
        language_code = request.POST['select-language']
        if language_code == '#':
            return render(request, 'localization/select_language.html', { 'content_id' : content_id, 'languages' : LANGUAGES, 'next' : get_redirect_url(request), 'error' : True })
        _export_backend(request, content_id, language_code)
        messages.info(request, 'Xliff document creation will now run in background. Once it is completed you will be notified by email')
        return get_redirect(request)
    return render(request, 'localization/select_language.html', { 'content_id' : content_id, 'languages' : LANGUAGES, 'next' : get_redirect_url(request) })

def _export_backend(request, content_id, language_code):
    trigger_backend_task("/localization/export/%(content_id)s/%(user_id)s/%(language_code)s" % {
                              'content_id' : content_id,
                              'user_id' : request.user.id,
                              'language_code' : language_code
                              }, target=get_versioned_module('localization'), queue_name='localization')

@backend
def export(request, content_id, user_id, language_code):
    user = get_object_or_404(User, pk=user_id)
    try:
        base_xml = ContentXML(content_id)
        pages = base_xml.get_pages_for_translation()
        xliff = Xliff(get_xliff())
        xliff.insert_texts_for_translation(pages, content_id)
        xliff.insert_metadata_element(content_id)
        xliff.set_target_language(language_code)
        uploaded_file = create_upload_file(xliff, content_id)
        send_export_success_notification(user, content_id, uploaded_file.pk)
    except Exception:
        import traceback
        send_export_failure_notification(user, content_id)
        logging.exception('Xliff export failed')
        mail_admins('Xliff export failed', traceback.format_exc())
    
    return HttpResponse("ok")

@login_required
def create_import(request, space_id):
    next_url = request.REQUEST['next'] if 'next' in request.REQUEST else '/mycontent'
    if request.method == 'POST':
        if len(request.FILES) > 0:
            _import_backend(request, space_id)
            messages.info(request, 'Xliff document import will now run in background. Once it is completed you will be notified by email')
            return HttpResponseRedirect(next_url)
        else:
            messages.error(request, 'File cannot be empty.')
            return HttpResponseRedirect(request.path)
    else:
        return render(request, 'localization/import_xliff.html',
                      {
                       'form' : get_upload_form(),
                       'upload_url' : get_upload_url(request.path),
                       'space' : get_space(space_id),
                       'next' : next_url
                       })
        
def _import_backend(request, space_id):
    uploaded_file = get_uploaded_file(request)
    trigger_backend_task("/localization/import/%(space_id)s/%(user_id)s/%(uploaded_file_id)s" % {
                     'space_id' : space_id,
                     'user_id' : request.user.id,
                     'uploaded_file_id' : uploaded_file.id
                      }, target=get_versioned_module('localization'), queue_name='localization')
    
@backend
def import_xliff(request, space_id, user_id, uploaded_file_id):
    user = get_object_or_404(User, pk=user_id)
    content_id = None
    contentXML = None
    try:
        uploaded_xliff = get_uploaded_xliff(uploaded_file_id)
        xliff = Xliff(uploaded_xliff)
        content_id = xliff.get_content_id()
        metadata = xliff.get_metadata_from_metadata_element()
        group_nodes = xliff.get_group_elements(lambda x: x.getAttribute('id') != 'metadata|metadata')
        pages = xliff.get_pages_with_modules_and_fields(group_nodes)
        contentXML = ContentXML(content_id)
        contentXML.set_translated_texts(pages, user)
        copy = make_copy_and_put_into_space(space_id, content_id, user, contentXML)
        copy.set_metadata(metadata)
        send_import_success_notification(user, copy.pk, contentXML.errors)
    except ContentException as xxx_todo_changeme:
        (instance) = xxx_todo_changeme
        send_import_failure_notification(user, [instance.parameter])
    except NodeNotFoundException as xxx_todo_changeme1:
        (instance) = xxx_todo_changeme1
        send_import_failure_notification(user, [instance.parameter])
    except xml.parsers.expat.ExpatError:
        send_import_failure_notification(user, ['Invalid document. Only Xliff documents allowed.'])
    except NoModulesFoundException as xxx_todo_changeme2:
        (instance) = xxx_todo_changeme2
        send_import_failure_notification(user, [instance.parameter])
    except Exception:
        import traceback
        logging.exception('Xliff import failed')
        mail_admins('Xliff import failed', traceback.format_exc())
        send_import_failure_notification(user, contentXML.errors if contentXML else ['Other system error'])
        
    return HttpResponse("ok")

def _create_version_control(content, user):
    # base XML
    content.file = create_new_version(content.file, user)
    if content.file.history_for is None:
        content.file.history_for = content
        content.file.save()

    # XLIFF file
    content.xliff_file = create_new_version(content.xliff_file, user)
    if content.xliff_file.history_for is None:
        content.xliff_file.history_for = content
    xliff_document = minidom.parseString(content.xliff_file.contents)
    xliff = Xliff(xliff_document)
    xliff.set_localized_version(content.file.version)
    xliff.set_original_version(content.original.file.version)
    content.xliff_file.contents = xliff.print_document()
    content.xliff_file.save()

@login_required
def show_versions(request, content_id):
    content = get_content(content_id)
    history = FileStorage.objects.filter(history_for=content, content_type='application/x-xliff+xml')
    return render(request, 'localization/show_versions.html', { 'versions' : history })


@login_required
@IsBeingEdited()
def check_versions(request, content_id):
    content = get_content(content_id)
    content.set_user_is_editing(request.user)
    xliff_document = minidom.parseString(content.xliff_file.contents)
    xliff = Xliff(xliff_document)
    is_localized_up_to_date = xliff.get_localized_version() == content.file.version
    is_original_up_to_date = xliff.get_original_version() == content.original.file.version
    if not is_localized_up_to_date or not is_original_up_to_date:
        lesson_type = 'Current' if not is_localized_up_to_date else 'Original'
        return render(request, 'localization/confirm_editor.html',
                      {
                       'content_id' : content_id,
                       'next_url' : get_redirect_url(request),
                       'lesson_type' : lesson_type
                       })
    return editor(request, content_id)


@login_required
def check_repeated_ids(request, content_id):
    confirmed = request.GET.get('confirmed', None)
    back_url = get_redirect_url(request)
    editor_token = request.GET.get('token_mycontent_editor', '---')
    if confirmed:
        return HttpResponseRedirect('/localization/check_versions/%s?next=%s&token_mycontent_editor=%s' % (content_id, back_url, editor_token))

    repeated_ids = _get_repeated_ids(content_id)

    if len(repeated_ids) > 0:
        return render(request, 'localization/check_repeated_ids.html', {
                            'repeated_ids' : repeated_ids,
                            'back_url' : back_url,
                            'content_id' : content_id
                      })

    return HttpResponseRedirect('/localization/check_versions/%s?next=%s&token_mycontent_editor=%s' % (content_id, back_url, editor_token))


def _get_repeated_ids(content_id):
    repeated_ids = []
    content = get_content(content_id)
    doc = minidom.parseString(content.file.contents)
    pages_nodes = doc.getElementsByTagName('page')
    for page_node in pages_nodes:
        page_id = page_node.getAttribute('href')
        page_file = FileStorage.objects.get(pk = page_id)
        page_doc = minidom.parseString(page_file.contents)
        modules_node = page_doc.getElementsByTagName('modules')
        modules_nodes = modules_node[0].childNodes if len(modules_node) > 0 else []
        ids = []
        for module_node in modules_nodes:
            if module_node.nodeType != minidom.Node.ELEMENT_NODE:
                continue
            module_id = module_node.getAttribute('id')
            if module_node.getAttribute('id') in ids:
                repeated = {
                    'id' : module_id,
                    'page' : page_node.getAttribute('name')
                }
                repeated_ids.append(repeated)
            else:
                ids.append(module_id)
    return repeated_ids

@login_required
def editor(request, content_id):
    localized_content = get_content(content_id)
    _create_version_control(localized_content, request.user)
    localized_content.modified_date = datetime.datetime.now()
    localized_content.save()
    xliff_file = localized_content.xliff_file
    xliff = Xliff(minidom.parseString(xliff_file.contents))
    groups = xliff.get_group_elements(lambda x: x.getAttribute('id') != 'metadata|metadata')
    pages = xliff.get_pages_with_modules_and_fields(groups)
    original_title = xliff.get_metadata_from_metadata_element()['title']
    close_url = '/localization/close/%(content_id)s?next=%(next)s' % { 'content_id' : content_id, 'next' : get_redirect_url(request) }
    return render(request, 'localization/editor.html', {
                   'pages' : pages,
                   'original_title' : original_title,
                   'localized_content' : localized_content,
                   'close_url' : close_url
                   })

@login_required
def close(request, content_id):
    content = Content.get_cached_or_404(id=content_id)
    xliff_document = minidom.parseString(content.xliff_file.contents)
    xliff = Xliff(xliff_document)
    group_nodes = xliff.get_group_elements(lambda x: x.getAttribute('id') != 'metadata|metadata')
    pages = xliff.get_pages_with_modules_and_fields(group_nodes)
    content_xml = ContentXML(content_id)
    content_xml.set_translated_texts(pages, request.user)
    content.file.contents = content_xml.print_document()
    content.file.save()
    content.stop_editing(request.user)
    return HttpResponseRedirect(get_redirect_url(request))

@login_required
def start_localization(request, content_id, space_id):
    content = Content.get_cached_or_404(id = content_id)
    projects = list(request.user.divisions.values())
    go_back = get_redirect_url(request)
    return render(request, 'localization/select_project_for_localization.html', {
                   'projects' : projects,
                   'content' : content,
                   'go_back' : go_back,
                   'space_id' : space_id
                   })

@login_required
def reset_xliff_to_current(request, content_id):
    content = get_content(content_id)
    xml_base = ContentXML(content.id)
    xliff = xml_base.make_xliff_object()
    xliff.set_localized_version(content.file.version)
    xliff.set_original_version(content.original.file.version)
    content.xliff_file.contents = xliff.print_document()
    content.xliff_file.save()
    messages.info(request, 'XLIFF document has been reseted to current.')
    return get_redirect(request)

@login_required
def reset_xliff_to_original(request, content_id):
    content = get_content(content_id)
    xml_base = ContentXML(content.original.id)
    xliff = xml_base.make_xliff_object()
    xliff.set_content_id(content.original)
    xliff.set_localized_version(content.file.version)
    xliff.set_original_version(content.original.file.version)
    content.xliff_file.contents = xliff.print_document()
    content.xliff_file.save()
    messages.info(request, 'XLIFF document has been reseted to original.')
    return get_redirect(request)

@login_required
def create_xliff_trigger(request, content_id, project_id):
    _create_xliff_backend(request, content_id, project_id)
    messages.info(request, 'Xliff document creation will now run in background. Once it is completed you will be notified by email')
    return get_redirect(request)

def _create_xliff_backend(request, content_id, project_id):
    trigger_backend_task("/localization/create_xliff/%(content_id)s/%(project_id)s/%(user_id)s" % {
                              'content_id' : content_id,
                              'project_id' : project_id,
                              'user_id' : request.user.id
                              }, target=get_versioned_module('localization'), queue_name='localization')

@backend
def create_xliff(request, content_id, project_id, user_id):
    user = get_object_or_404(User, pk = user_id)
    try:
        xml_base = ContentXML(content_id)
        xliff = xml_base.make_xliff_object()
        xliff.set_localized_version(1)
        original = get_content(content_id)
        xliff.set_original_version(original.file.version)
        xliff.validate_size()
        localization_content = make_copy_and_put_into_space(project_id, original.id, user, xml_base)
        localization_content.original = original
        localization_content.xliff_file = create_xliff_filestorage(user, xliff.print_document())
        localization_content.save()
        localization_content.xliff_file.history_for = localization_content
        localization_content.xliff_file.save()
        send_create_xliff_success_notification(user, content_id, project_id)
    except ContentTooBigException:
        send_content_too_big_notification(user, original)
    except Exception:
        import traceback
        send_create_xliff_failure_notification(user, content_id)
        mail_admins('Xliff export failed', traceback.format_exc())
    return HttpResponse('ok')

@login_required
def save_field(request):
    rp = request.POST
    content_id = rp.get('content_id')
    value = rp.get('value')
    group_id = rp.get('page_id')
    group_name = rp.get('page_name')
    module = Module(rp.get('module_id'), rp.get('module_name'))
    name = rp.get('field_name')
    list_name = rp.get('list_name') if rp.get('list_name') != 'None' else None
    list_index = rp.get('list_index') if rp.get('list_index') != 'None' else None
    field_type = rp.get('type') if rp.get('type') != 'None' else None
    
    field = Field(value, name, field_type, list_name, list_index)
    trans_unit_id = create_id_string(field, module)
    content = Content.get_cached_or_none(id=content_id)
    
    xliff_document = minidom.parseString(content.xliff_file.contents)
    xliff = Xliff(xliff_document)
    xliff.set_translated_content(value, group_id, trans_unit_id)
    xliff.set_translated_page_name(group_name, group_id)
    
    content.xliff_file.contents = xliff.print_document()
    content.xliff_file.save()
    
    return HttpResponse('OK')

@login_required
def compare(request, content_id):
    localized = get_content(content_id)
    
    return render(request, 'localization/show_differences.html', {'localized' : localized, 'back_url' : get_redirect_url(request)})

@login_required
def update_lesson(request, content_id):
    localized = get_content(content_id)
    localizedXML = ContentXML(content_id)
    originalXML = ContentXML(localized.original.id)
    
    localized_pages = localizedXML.get_pages_for_translation()
    original_pages = originalXML.get_pages_for_translation()
    
    comparer = Comparer(localized.original, original_pages, localized, localized_pages)
    
    comparer.compare()
    
    for difference in comparer.differences:
        localizedXML.update(difference, originalXML, request.user)
    
    messages = ','.join(comparer.get_messages())
    
    return HttpResponse(content=messages, status=200)
