# -*- coding: utf-8 -*-
import json
import uuid

from django.template.loader import render_to_string
from django.utils.translation import get_language_info
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import get_object_or_404, render
from django.views.generic.base import TemplateView
from google.appengine.runtime import DeadlineExceededError
from lorepo.api.v2.jwt_api import jwt_payload_handler, jwt_encode_handler
from lorepo.corporate.decorators import HasSpacePermissionMixin
from lorepo.embed.decorators import check_is_public
from lorepo.filestorage.forms import UploadForm
from lorepo.filestorage.models import FileStorage, UploadedFile
from lorepo.mycontent.fix_ssl import ContentFixer
from lorepo.mycontent.forms import ContentMetadataForm, AddonMetadataForm,\
    AddAddonForm
from lorepo.mycontent.lesson.update_content_template import update_content_template
from lorepo.mycontent.models import Content, ContentType,\
    SpaceTemplate, DefaultTemplate, UpdateTemplateStatus, CurrentlyEditing,\
    ContentSpace
import datetime
from lorepo.spaces.models import Space, SpaceType, SpaceAccess
from lorepo.spaces.util import get_user_spaces, \
      get_spaces_for_copy,  get_private_space_for_user, get_spaces_tree,\
      change_contentspace, _get_subspaces, is_company_locked
from lorepo.spaces.util import get_space_for_content
from lorepo.spaces.util import get_spaces_path_for_content
from lorepo.mycontent.util import get_addon_source_code, create_template_node,\
    clean_content_assets, save_recently_opened, get_content_with_changed_content_file
from lorepo.filestorage.utils import create_new_version, resize_image
from lorepo.filestorage.views import get_file
from libraries.utility.redirect import get_redirect_url, get_redirect
import re
from lorepo.token.decorators import cached_token
from lorepo.mycontent.service import add_content_to_space,\
    update_content_space, remove_content_space
from lorepo.token.models import TOKEN_KEYS
from lorepo.token.util import create_mycontent_editor_token, create_mycontent_edit_addon_token
from mauthor.customfixdb.models import FixLog
from mauthor.states.models import ProjectStatesSet, ContentState
from mauthor.states.util import get_states_sets
from django.contrib import messages
import libraries.utility.cacheproxy as cache
from lorepo.permission.decorators import has_space_access, company_locked
from lorepo.corporate.utils import get_publication_for_space, get_contents,\
    get_division_for_space
from mauthor.utility.decorators import LoginRequiredMixin
from querystring_parser import parser
from lorepo.permission.models import Permission
from google.appengine.ext import blobstore
from lorepo.mycontent.signals import addon_published, addon_deleted,\
    metadata_updated
import urllib.request, urllib.parse, urllib.error
import logging
from libraries.utility.helpers import parse_query_dict
from django.contrib.auth.models import User
from lorepo.permission.util import verify_content_access, verify_space_access
from lorepo.permission.notifications import send_no_access_notification
from lorepo.public.util import send_message
import settings
from django.core.mail import mail_admins
from libraries.utility.queues import trigger_backend_task, trigger_backend_tasks
from mauthor.metadata.util import save_metadata_from_request, toggle_page_metadata, update_page_metadata,\
    get_page_metadata, get_metadata_values_and_definitions, copy_metadata
from mauthor.metadata.models import MetadataValue, PageMetadata
from libraries.core.paginator import CustomPaginator
from lorepo.mycontent.decorators import is_being_edited
from lorepo.mycontent.util import set_new_token_and_return_path
from libraries.utility.decorators import backend
from libraries.utility.environment import get_versioned_module
from mauthor.utility.db_safe_iterator import safe_iterate
from google.appengine.api import urlfetch


def trash(request, space_id=None):
    return _index(request, space_id, True)


@login_required
@company_locked
@has_space_access(Permission.CONTENT_VIEW)
def index(request, space_id=None):
    return _index(request, space_id, False)


def _index(request, space_id=None, is_trash=False):
    copy_spaces = get_spaces_for_copy(request.user)
    if space_id is None:
        space_request = get_private_space_for_user(request.user)
    else:
        space_id = int(space_id)
        space_request = Space.objects.get(id=space_id)

    header = None
    if space_request and space_request.is_corporate():
        spaces = get_spaces_tree(space_id)
        header = space_request.top_level.title
    else:
        spaces = get_user_spaces(request.user)

    subheader = None
    if not space_request.is_top_level():
        subheader = space_request.title

    subspaces = None
    if space_id != 0:
        subspaces = _get_subspaces([space_request])
        subspaces.add(space_request)

    set_order_by_cookie = False
    order_by = request.GET.get('order_by')
    if order_by not in ['title', '-title', 'modified_date', '-modified_date']:
        #get this setting from COOKIE
        order_by = request.COOKIES.get('mycontent_list_order_by','-modified_date')
    else:
        set_order_by_cookie = True

    content_list = get_contents(space_request, is_trash, order_by)
    
    page_number = int(request.GET.get('page')) if 'page' in request.GET and re.search("^[\d]+$", request.GET.get('page')) else 0
    paginator = CustomPaginator(content_list, 10)
    page_content = paginator.page(page_number)
    
    page_contents = []
    for item in page_content.object_list:
        page_contents.append(item)

    sub_menus = [
        ('Create Lesson','/mycontent/addcontent/%(space_id)s?next=/mycontent/%(space_id)s' % {'space_id': space_request.id}),
        ('Create Addon', '/mycontent/addon/%(space_id)s?next=/mycontent/%(space_id)s' % { 'space_id' : space_request.id }),
        ('Import Lesson', '/exchange/import/%(space_id)s?next=/mycontent/%(space_id)s' % { 'space_id' : space_request.id }),
        ('Import XLIFF', '/localization/create_import/%(space_id)s?next=/mycontent/%(space_id)s' % { 'space_id' : space_request.id }),
        ('Import InDesign XML (Beta)', '/indesign/upload/%(space_id)s?next=/mycontent/%(space_id)s' % { 'space_id' : space_request.id }),
        ('Import PDF (Beta)', '/pdfimport/upload/%(space_id)s?next=/mycontent/%(space_id)s' % { 'space_id' : space_request.id })
    ]

    editor_token, editor_token_key = create_mycontent_editor_token(request.user)
    addon_token, addon_token_key = create_mycontent_edit_addon_token(request.user)
    resp = render(request, 'mycontent/index.html',
                  {
                      'contents': page_contents,
                      'paginator': paginator,
                      'spaces': sorted(list(spaces), key=lambda space: space.title),
                      'copy_spaces': sorted(list(copy_spaces), key=lambda space: space.title),
                      'space_request': space_request,
                      'is_trash': is_trash,
                      'header': header,
                      'subheader': subheader,
                      'current_page': page_content,
                      'sub_menus': sub_menus,
                      'space_id': space_id,
                      'has_more_actions_permissions': True,
                      'is_owner': True,
                      'editor_token': editor_token,
                      'editor_token_key': editor_token_key,
                      'addon_token': addon_token,
                      'addon_token_key': addon_token_key,
                      'extra_params': {'order_by': order_by},

                  })
    if set_order_by_cookie:
        resp.set_cookie('mycontent_list_order_by',value=order_by, max_age=60*60*24*30)
    return resp

@login_required
@has_space_access(Permission.CONTENT_EDIT)
def add_content(request, space_id=None):
    form = None
    if request.method == 'POST':
        form = ContentMetadataForm(request.POST)
        next_url = form.data['next'] if 'next' in form.data else '/mycontent/'

        if form.is_valid():
            now = datetime.datetime.now()
            st = SpaceTemplate.objects.filter(space=request.user.company)
            dt = DefaultTemplate.objects.all()

            icon_href = None
            # Get template
            if 'template' in form.data and form.data['template']:
                template = Content.get_cached(id=form.data['template'])
                contents = create_template_node(template.file, request.user)
                icon_href = template.icon_href
            elif len(st) > 0:
                template = st[0].template
                contents = create_template_node(template.public_version, request.user)
                icon_href = template.icon_href
            elif len(dt) > 0:
                template = dt[0].template
                contents = create_template_node(template.file, request.user)
                icon_href = template.icon_href
            else:
                # Add empty page
                t = render_to_string('initdata/lesson/page.xml', {}).encode('utf-8')
                pageFile = FileStorage(
                                       created_date = now,
                                       modified_date = now,
                                       content_type = "text/xml",
                                       contents = t,
                                       owner = request.user)
                pageFile.save()
                
                params = {'page' : pageFile }
                # Add empty content file
                contents = render_to_string('initdata/lesson/content.xml', params).encode('utf-8')

            contentFile = FileStorage(
                                   created_date = now,
                                   modified_date = now,
                                   content_type = "text/xml",
                                   contents = contents,
                                   owner = request.user)
            contentFile.version = 1
            contentFile.save()

            # Register content in database
            content = Content(
                            created_date = now, 
                            modified_date = now, 
                            author = request.user,
                            file = contentFile,
                            icon_href = icon_href)
            content.set_metadata(form.cleaned_data)
            content.add_title_to_xml()
            content.set_score_type(form.cleaned_data['score_type'])
            content.save()
            contentFile.history_for = content
            contentFile.save()

            # Add connection between content and user via space
            if space_id is None:
                space = get_private_space_for_user(request.user)
            else:
                space = Space.objects.get(pk=space_id)

            states_sets_dict = get_states_sets(request.user.company)
            project_states_set = ProjectStatesSet.objects.filter(project=space)
            if len(project_states_set) > 0:
                pss = project_states_set[0]
                first_state = states_sets_dict[pss.states_set][0]
                cs = ContentState(state=first_state, content=content)
                cs.is_current = True
                cs.save()
            add_content_to_space(content, space)

            token, token_key = create_mycontent_editor_token(request.user)

            payload = jwt_payload_handler(request.user)
            jwt_token = jwt_encode_handler(payload)

            try:
                result = urlfetch.fetch(url = 'https://newinterface-dot-lorepocorporate.appspot.com/api/v2/my_content/refresh_content_index/%s' % content.pk, method = urlfetch.POST, headers = {'Authorization': 'JWT %s' % jwt_token})
                if result.status_code != 200:
                   logging.error("Fetch url error %s" % content.pk)
            except:
                import traceback
                logging.error("Something went wrong %s" % content.pk)
                logging.error(traceback.format_exc())


            redirect_url = '/mycontent/{}/editor?new=1&next={}&{}={}'.format(str(content.pk), next_url, token_key, token)

            return HttpResponseRedirect(redirect_url)
    else:
        next_url = request.GET.get('next', '/mycontent/')

    return render(request, 'mycontent/addcontent.html', {'space_id' : space_id, 'form' : form, 'next' : next_url})


@login_required
@has_space_access(Permission.CONTENT_EDIT)
def addon(request, space_id = None):
    if request.method == 'POST':
        form = AddAddonForm(request.POST)
        next_url = form.data['next'] if 'next' in form.data else '/mycontent/'
        if form.is_valid():
            now = datetime.datetime.now()

            # Store the file
            addon_file = FileStorage(
                                   created_date = now,
                                   modified_date = now,
                                   content_type = "text/xml",
                                   contents = "",
                                   owner = request.user)
            addon_file.save()

            # Register content in database
            content = Content(
                            title=form.cleaned_data['title'],
                            tags=form.cleaned_data['tags'],
                            description=form.cleaned_data['description'], 
                            short_description=form.cleaned_data['short_description'],
                            name=form.cleaned_data['name'],
                            created_date = now, 
                            modified_date = now, 
                            author = request.user,
                            content_type = ContentType.ADDON,
                            file = addon_file)
            content.save()

            t = render_to_string('initdata/addon/addon.xml', {'addonId' : content.name}).encode('utf-8')
            addon_file.contents = t
            addon_file.version = 1
            addon_file.history_for = content
            addon_file.save()

            # Add connection between content and user via space
            if space_id is None:
                space = get_private_space_for_user(request.user)
            else:
                space = Space.objects.get(pk=space_id)

            add_content_to_space(content, space)

            metadata_updated.send(sender=None, content_id=content.id)

            return HttpResponseRedirect(next_url)
    else:
        form = AddAddonForm()

    return render(request, 'mycontent/add_addon.html', {'space_id' : space_id, 'form' : form, 'next' : get_redirect_url(request)})

@login_required
@has_space_access(Permission.CONTENT_EDIT_METADATA)
def addon_metadata(request, addon_id):
    addon = Content.get_cached_or_404(id=addon_id)
    
    if request.POST:
        form = AddonMetadataForm(request.POST)
        
        if form.is_valid():
            addon.title = form.cleaned_data['title']
            addon.tags = form.cleaned_data['tags']
            addon.description = form.cleaned_data['description']
            addon.short_description = form.cleaned_data['short_description']
            addon.modified_date = datetime.datetime.now()
            addon.save()
            return HttpResponseRedirect(form.data['next'])
    else:
        form = AddonMetadataForm()
        form.initialize(addon)
        
    next_url = request.GET.get("next") if request.GET.get("next") else form.data['next']
    return render(request, 'mycontent/addon_metadata.html', {
        'form': form,
        'addon': addon,
        'next': next_url
    })


@cached_token(TOKEN_KEYS.MYCONTENT_EDIT_ADDON)
@has_space_access(Permission.CONTENT_EDIT)
@is_being_edited
def edit_addon(request, addon):
    next_url = request.GET.get('next')
    publish_url = None
    create_new_version_url = None
    addon.file = create_new_version(addon.file, request.user, True)
    if addon.file.history_for is None:
        addon.file.history_for = addon
        addon.file.save()
    addon.save()
    
    content_space = ContentSpace.objects.get(content=addon)
    space = content_space.space
    if space.space_type == SpaceType.CORPORATE:
        if verify_space_access(space, request.user, Permission.CONTENT_MAKE_PUBLIC):
            if get_division_for_space(space).include_contents_in_editor:
                publish_url = '/corporate/%s/publish' % addon.pk
                create_new_version_url = '/corporate/%s/newVersion' % addon.pk

    redirect_to = "/mycontent/%s/exit_editor?next=%s" % (addon.pk, next_url)

    return render(request, 'mycontent/edit_addon_content.html',
                  {"content": addon, 'next_url': redirect_to, 'publish_url': publish_url, 
                   'create_new_version_url': create_new_version_url})

@login_required
@has_space_access(Permission.CONTENT_EDIT)
@cached_token(TOKEN_KEYS.MYCONTENT_EDITOR)
@is_being_edited
def editor(request, content):
    nextUrl = request.GET.get('next')
    if nextUrl:
        nextUrl = urllib.parse.quote_plus(nextUrl)
    else:
        nextUrl = ''
    old_version = 0
    if not request.GET.get("new"):
        old_version = content.file.id
        content.file = create_new_version(content.file, request.user)
        if content.file.history_for is None:
            content.file.history_for = content
            content.file.save()
    content.save()
    save_recently_opened(request.user, content)
    space = get_space_for_content(content)
    if space.is_project():
        editor_title = _get_title_for_project_editor(content, space)
    else:
        editor_title = _get_title_for_editor2(content, space)

    redirect_to = "/mycontent/%s/exit_editor?next=%s" % (content.pk, nextUrl)

    return render(request, 'mycontent/editor.html', {"content" : content,
                                                     'exitUrl' : redirect_to,
                                                     'space_id' : space.id,
                                                     'title': editor_title['title'],
                                                     'sub_title': editor_title['sub_title'],
                                                     'nextUrl' : nextUrl,
                                                     'old_version': old_version,
                                                     'favourite_modules': request.user.profile.favourite_modules,
                                                     'should_render_view': request.user.profile.render_view,
                                                     'language': request.user.profile.language_code
                                                     })


def _get_title_for_editor(content, space):
    template = content.get_template()
    lesson_title = "<b>Lesson:</b> %s | <b>Template:</b> %s" % (content.title, template or 'None')

    if not space.is_corporate():
        return {'title': lesson_title, 'sub_title': ''}

    publication = get_publication_for_space(space)
    project = publication.parent

    return {'title': "<b>Project:</b> %s | <b>Publication:</b> %s" % (project, publication),
            'sub_title': lesson_title}

def _get_title_for_project_editor(content, space):
    template = content.get_template()
    title = content.title
    sub_title = "Template: <span id=\"spaceName\">%s</span>" % template or 'None'

    if space.is_corporate():
        sub_title += " Project: <span id=\"projectName\">%s</span>" % space
        sub_title += " Publication: <span id=\"publicationName\">%s</span>" % space

    return {'title': title, 'sub_title': sub_title}

def _get_title_for_editor2(content, space):
    template = content.get_template()
    title = content.title
    sub_title = "Template: <span id=\"spaceName\">%s</span>" % template or 'None'

    if space.is_corporate():
        publication = get_publication_for_space(space)
        project = publication.parent
        
        sub_title += " Project: <span id=\"projectName\">%s</span>" % project
        sub_title += " Publication: <span id=\"publicationName\">%s</span>" % publication

    return {'title': title, 'sub_title': sub_title}


@login_required
def exit_editor(request, content_id):
    content = get_object_or_404(Content, pk=content_id)
    update_page_metadata(content)
    content.stop_editing(request.user)
    content.save()
    metadata_updated.send(sender=None, content_id=content_id)

    return get_redirect(request)


def save_favourite_modules(request):
    if not request.user.is_authenticated():
        return HttpResponse('logged out', status=401)
    try:
        user_profile = request.user.profile
        user_profile.favourite_modules = json.dumps(json.loads(request.body).get('fav_modules', []))
        user_profile.save()
    except Exception:
        return HttpResponse('Wrong json', status=403)

    return HttpResponse("OK")


def save_should_render(request):
    if not request.user.is_authenticated():
        return HttpResponse('logged out', status=401)

    user_profile = request.user.profile
    user_profile.render_view = bool(int(request.POST.get('is_rendered', 1)))
    user_profile.save()

    return HttpResponse("OK")


@login_required
@has_space_access(Permission.CONTENT_VIEW)
def preview(request, content_id):
    context = {}
    content = Content.get_cached_or_404(id=content_id)
    context['content'] = content
    context['copy_spaces'] = get_spaces_for_copy(request.user)
    context['spaces'] = get_spaces_path_for_content(context['content'], lambda space: space.is_private() or space.is_corporate())
    context['non_public_spaces'] = context['spaces']
    context['tl_space'] = get_space_for_content(context['content'])
    context['is_public'] = False

    context['back_url'] = get_redirect_url(request)
    context['is_owner'] = True
    context['has_more_actions_permissions'] = True
    context['is_company_locked'] = is_company_locked(request.user.company)

    token, token_key = create_mycontent_editor_token(request.user)
    context['token'] = token
    context['token_key'] = token_key
    context['sub_menus'] = _get_preview_sub_menus(content, '/mycontent/view/%s?next=%s' % (content.id, context['back_url']), token, token_key)

    return render(request, 'mycontent/preview.html', context)


def _get_preview_sub_menus(content, back_url, token, token_key):
    sub_menus = [
        ('Edit Lesson', '/mycontent/%s/editor?next=%s&%s=%s' % (content.id, back_url, token_key, token), None),
        ('Edit Metadata', '/mycontent/%s/metadata?next=%s' % (content.id, back_url), None)
    ]

    if content.enable_page_metadata:
        sub_menus.append(('Edit Page Metadata', '/mycontent/%s/pagemetadata?next=%s' % (content.id, back_url), None))

    if content.is_content_public():
        sub_menus.append(('Unpublish', '/corporate/%s/makepublic?next=%s' % (content.id, back_url), None))
    else:
        sub_menus.append(('Publish', '/corporate/%s/makepublic?next=%s' % (content.id, back_url), None))

    sub_menus.append(('Delete Lesson', '/mycontent/%s/delete?next=/mycontent' % content.id, {
        'is_delete': True
    }))

    return sub_menus


@login_required
@has_space_access(Permission.CONTENT_VIEW)
def view_addon(request, addon_id):
    addon = Content.get_cached_or_404(id=addon_id)
    spaces = get_spaces_path_for_content(addon, lambda space: space.is_private() or space.is_corporate())
    addon_source = get_addon_source_code(addon.file.contents)
    return render(request, 'mycontent/preview_addon.html',
                  {
                   'addon' : addon, 
                   'spaces' : spaces, 
                   'copy_spaces' : get_spaces_for_copy(request.user),
                   'private_space' : get_private_space_for_user(request.user),
                   'view' : addon_source['view'],
                   'preview' : addon_source['preview'],
                   'presenter' : addon_source['presenter'],
                   'properties' : addon_source['properties']
                   })

def get_addon(request, addon_id):
    addon = get_object_or_404(Content, name=addon_id)
    return get_file(request, addon.file.id)

@login_required
@has_space_access(Permission.CONTENT_EDIT_METADATA)
@is_being_edited
def metadata(request, content):
    assigned_space = get_space_for_content(content)
    try:
        language_bidi = get_language_info(request.user.language_code_bidi)['bidi']
    except (KeyError, TypeError): #for some unknown reason on ocassion language_code_bidi is none
        language_bidi = False
    is_template = content.content_type == ContentType.TEMPLATE
    if request.method == 'POST':
        form = ContentMetadataForm(request.POST)
        if form.is_valid():
            content.set_metadata(form.cleaned_data)
            if 'is_template' in list(form.data.keys()):
                content.content_type = ContentType.TEMPLATE
            else:
                content.content_type = ContentType.LESSON
            if 'enable_page_metadata' in list(form.data.keys()):
                toggle_page_metadata(content, True)
                update_page_metadata(content)
            else:
                toggle_page_metadata(content, False)
            content.passing_score = form.cleaned_data['passing_score']
            content.modified_date = datetime.datetime.now()
            content.add_title_to_xml()
            content.set_score_type(form.cleaned_data['score_type'])
            content.save()
            space_id = form.data['space_id']
            change_contentspace(content, space_id, False)
            cache.delete('templates_for_%s' % (request.user))

            save_metadata_from_request(request, content)
            metadata_updated.send(sender=None, content_id=content.id)

            messages.success(request, 'Metadata successfully saved')
            return HttpResponseRedirect(form.data['next'])
        else:
            space_id = int(form.data['space_id'])
            if space_id != 0:
                assigned_space = Space.objects.get(pk=space_id)
            is_template = True if 'is_template' in list(form.data.keys()) else False
    else:
        form = ContentMetadataForm()
        form.initialize(content)

    next_url = request.GET.get("next") if request.GET.get("next") else form.data['next']

    spaces = get_spaces_tree(assigned_space.id)

    metadata_values = get_metadata_values_and_definitions(content, request.user.company)

    return render(request, 'mycontent/metadata.html', 
                  { 
                    'content'       : content,
                    'spaces'        : sorted(list(spaces), key=lambda space: space.title),
                    'priv_space'    : assigned_space, 
                    'form'          : form,
                    'next'          : next_url,
                    'is_template'   : is_template,
                    'definitions'   : metadata_values,
                    'content_id'    : str(content.id),
                    'language_bidi' : language_bidi
                    })

@login_required
def cancel_editing(request, content_id):
    content = Content.get_cached(id=content_id)
    content.stop_editing(request.user)
    return get_redirect(request)

@login_required
@has_space_access(Permission.CONTENT_EDIT_METADATA)
def pagemetadata(request, content_id):
    content = Content.get_cached_or_404(id=content_id)
    try:
        language_bidi = get_language_info(request.user.language_code_bidi)['bidi']
    except KeyError: #for some unknown reason on ocassion language_code_bidi is none
        language_bidi = False
    if request.method == 'POST':
        parameters = parse_query_dict(request.POST)
        for id in list(parameters.ids.keys()):
            pagemetadata = PageMetadata.objects.get(pk=id)
            pagemetadata.tags = parameters.tags[id][0]
            pagemetadata.short_description = parameters.short_description[id][0]
            pagemetadata.description = parameters.description[id][0]
            pagemetadata.save()
            MetadataValue.objects.filter(content=content, page=pagemetadata).delete()
            if 'type' in parameters.__dict__:
                types = parameters.type[id]
                names = parameters.name[id]
                descriptions = parameters.metadata_description[id]
                values = parameters.values[id]
                unused_flags = parameters.unused[id]
                entered_value = parameters.entered_value[id] if id in parameters.entered_value else ''
                for counter, current_type in enumerate(types):
                    if unused_flags[counter]=='false':
                        definition = MetadataValue(company=request.user.company,
                                                field_type=current_type,
                                                name=names[counter],
                                                description=descriptions[counter],
                                                value=values[counter],
                                                order=counter,
                                                content=content,
                                                entered_value=entered_value[counter],
                                                page=pagemetadata,
                                                is_enabled=True)
                        definition.save()
        content.save()
        metadata_updated.send(sender=None, content_id=content_id)
        messages.info(request, 'Page Metadata for lesson %s has been saved.' % content.title)
        return get_redirect(request)
    pagemetadata = get_page_metadata(content, request.user.company)
    return render(request, 'metadata/pagemetadata.html',
                  {
                   'content' : content,
                   'pagemetadata' : pagemetadata,
                   'language_bidi': language_bidi,
                   'next_url' : get_redirect_url(request)
                   })

@login_required
@has_space_access(Permission.CONTENT_ICON)
def changeIcon(request, content_id):
    return _changeIcon(request, content_id, (146, 109))

@login_required
@has_space_access(Permission.CONTENT_ICON)
def changeAddonIcon(request, content_id):
    return _changeIcon(request, content_id, (64, 64))

def _changeIcon(request, content_id, size):
    """
    Handler wywolywany po uploadzie ikony podgladu contentu
    """
    content = Content.get_cached_or_404(id=content_id)
    if size[0] == 64:
        upload_url = blobstore.create_upload_url('/mycontent/' + str(content.id) + '/change_addon_icon')
    else:
        upload_url = blobstore.create_upload_url('/mycontent/' + str(content.id)+ '/changeicon')
        
    form = UploadForm()
      
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if len(request.FILES) > 0: 
            model = form.save(False)
            model.owner = request.user
            
            filename = request.FILES['file'].name
            content_type = request.FILES['file'].content_type
            m = re.search('\.(gif|png|jpg|jpeg|webp|bmp|ico|tiff|tif)$', filename)
            if m:
                ext = m.group(0)
                if ext != '.png':
                    filename = filename.replace(ext, '.png')
                    content_type = 'image/png'

            model.content_type = content_type
            model.filename = filename

            model.save()
            model.path = resize_image(model, size[0], size[1])
            model.file = str(blobstore.create_gs_key('/gs' + model.path))
            model.save()
            content.modified_date = datetime.datetime.now()
            content.icon_href = "/file/serve/" + str(model.id)
            content.save()
            metadata_updated.send(sender=None, content_id=content_id)
            return HttpResponseRedirect(form.data["next"] if "next" in form.data else "/")
    next_url = request.GET.get('next') if 'next' in request.GET else form.data['next']  
        
    return render(request, 'mycontent/changeicon.html', 
                  {
                   "content" : content, 
                "upload_url" : upload_url,
                     "width" : size[0],
                    "height" : size[1],
                      "next" : next_url,
                      "form" : form
                })

@login_required
@has_space_access(Permission.CONTENT_COPY, token_key='copy_content')
def copy(request, content_id, space_id = None):
    if space_id is None:
        space = get_private_space_for_user(request.user)
    else:
        space = get_object_or_404(Space, id=space_id)

    content = Content.get_cached_or_404(id=content_id)
    copy = content.makeCopy(True, request.user)

    if copy.content_type != ContentType.ADDON:
        copy.add_title_to_xml()

    copy_metadata(content, copy)

    add_content_to_space(copy, space)

    payload = jwt_payload_handler(request.user)
    jwt_token = jwt_encode_handler(payload)

    try:
        result = urlfetch.fetch(
            url='https://newinterface-dot-lorepocorporate.appspot.com/api/v2/my_content/refresh_content_index/%s' % copy.pk,
            method=urlfetch.POST, headers={'Authorization': 'JWT %s' % jwt_token})
        if result.status_code != 200:
            logging.error("Fetch url error %s" % content.pk)
    except:
        import traceback
        logging.error("Something went wrong %s" % content.pk)
        logging.error(traceback.format_exc())

    metadata_updated.send(sender=None, content_id=copy.id)

    messages.success(request, 'Lesson <%s> copied' % content.title)

    space_id = space.id
    redirect_to = '/mycontent/%(space_id)s' % locals() if space.is_private() else '/corporate/list/%(space_id)s' % locals()

    return get_redirect(request, redirect_to)


@login_required
@check_is_public
def copy_public_lesson(request, content_id):
    content = Content.get_cached_or_404(id=content_id)
    if not content.is_globally_public:
        raise Http404
    copied_lesson = content.makeCopy(True, request.user)
    copy_metadata(content, copied_lesson)

    space = get_private_space_for_user(request.user)
    add_content_to_space(copied_lesson, space)

    metadata_updated.send(sender=None, content_id=copied_lesson.id)

    return HttpResponseRedirect('/mycontent/')


@login_required
@has_space_access(Permission.CONTENT_MAKE_PUBLIC)
def make_public(request, content_id):
    content = Content.get_cached_or_404(id=content_id)
    try:
        public_version = content.public_version
    except FileStorage.DoesNotExist:
        public_version = None
        content.is_public = False
    if public_version is None:
        content.public_version = content.file
    else:
        content.public_version = None

    content.is_public = not content.is_public

    user = content.who_is_editing()
    if content.is_public and user:
        return render(request, 'mycontent/publish_content_error.html',
                                  {
                                   'username' : user.username,
                                   'back' : get_redirect_url(request)
                                   })

    content.save()

    if content.content_type == ContentType.ADDON:
        addon_published.send(sender=None, company_id=request.user.company.id)

    return get_redirect(request)

@login_required
@has_space_access(Permission.CONTENT_MAKE_PUBLIC)
def make_globally_public(request, content_id):
    content = Content.get_cached_or_404(id=content_id)
    content.is_globally_public = not content.is_globally_public
    content.save()
    return get_redirect(request)

@login_required
@has_space_access(Permission.CONTENT_MAKE_PUBLIC)
def update_public(request, content_id, version):
    content = Content.get_cached_or_404(id=content_id)
    file_storage = FileStorage.objects.filter(history_for=content, version=version)[0]
    content.public_version = file_storage
    content.save()

    return get_redirect(request)

@login_required
@has_space_access(Permission.CONTENT_EDIT)
def make_template(request, content_id):
    content = Content.get_cached_or_404(id=content_id)
    if content.content_type == ContentType.TEMPLATE:
        content.content_type = ContentType.LESSON
    else:
        content.content_type = ContentType.TEMPLATE

    content.save()
    metadata_updated.send(sender=None, content_id=content_id)
    cache.delete('templates_for_%s' % (request.user))
    return get_redirect(request)

@login_required
@has_space_access(Permission.CONTENT_REMOVE)
def delete(request, content_id):
    now = datetime.datetime.now()
    content = Content.get_cached_or_404(id=content_id)
    content_space = [content_space for content_space in content.contentspace_set.all() if not content_space.space.is_public()][0]
    if content_space.space.is_top_level():
        content_space.is_deleted = not content_space.is_deleted
        update_content_space(content_space)
    else:
        add_content_to_space(content, content_space.space.top_level, is_deleted=True)
        remove_content_space(content_space)
    content.public_version = None
    content.modified_date = now
    content.content_type = ContentType.LESSON
    content.is_deleted = not content.is_deleted
    content.save()
    metadata_updated.send(sender=None, content_id=content_id)

    if content.content_type == ContentType.ADDON:
        addon_deleted.send(sender=None, company_id=request.user.company.id)

    return HttpResponseRedirect(get_redirect_url(request))

@login_required
@has_space_access(Permission.CONTENT_SHOW_HISTORY)
def show_history(request, content_id):
    content = Content.get_cached_or_404(id=content_id)
    versions = list(content.filestorage_set.filter(content_type='text/xml').order_by('-modified_date'))
    labels = {
        'template_change' : 'template replaced',
        'assets_update' : 'assets updated',
        'template_update': 'template updated',
        'assets_package': 'assets package',
        'schemeless_fix': 'references to unsafe URLS updated',
        'Hierarchical Lesson report fix': 'Hierarchical Lesson report fix',  # Fix on branch test-5707m
        'property_fix_v2': 'Hierarchical Lesson report fix update',
        'property_fix_v3': 'Hierarchical Lesson report fix update',
        'properties_changer': 'Changed by properties changer'
    }
    for version in versions:
        try:
            meta = json.loads(version.meta)
            version.comment = labels[meta['comment']]
        except:
            pass

    return render(request, 'mycontent/history.html',
                  {
                    'content' : content,
                   'versions' : versions,
                   })


@login_required
@user_passes_test(lambda u: u.is_superuser)
def fix_ssl(request, content_id):
    content = Content.get_cached_or_404(id=content_id)
    fixer = ContentFixer(content, request.user)
    check_result = fixer.check_external_resources()
    if check_result['status'] == 0:
        messages.info(request, check_result['message'])
    else:
        messages.error(request, check_result['message'], extra_tags='danger')
    return get_redirect(request, target=request.META.get('HTTP_REFERER', '/mycontent'))


@login_required
@user_passes_test(lambda u: u.is_superuser)
def check_ssl_space(request, space_id):
    trigger_backend_task('/mycontent/check_ssl_space_backend/%s' % space_id)
    messages.info(request, 'Triggered!')
    return HttpResponseRedirect('/mycontent')


def _check_contents(queryset, report_file):
    fixable_contents_count = 0
    all_contents_count = 0
    for batch in safe_iterate(queryset):
        report = ''
        for content in batch:
            if content.is_deleted:
                continue
            all_contents_count += 1
            try:
                fixer = ContentFixer(content)
                check = fixer.check_external_resources()
                if check['status'] == 0:
                    continue
                fixable_contents_count += 1
                report += '%(id)s\t%(content_id)s\t%(fix_styles)s\t%(fix_pages)s\t%(title)s\n' % check
            except Exception as e:
                logging.error('Error in content %s: %s' % (content.id, e))
        report = str(report.encode('utf-8'))
        report_file.write(report)
    return fixable_contents_count, all_contents_count


@backend
def check_ssl_space_backend(request, space_id):
    space = Space.objects.get(pk=space_id)
    slug = 'test_ssl_'
    if space.is_corporate():
        preview_prefix = 'corporate/ssl_report'
        slug += 'corporate'
    else:
        preview_prefix = 'mycontent/ssl_report'
        slug += 'private'
    logger = FixLog.start(slug)
    log_data = {
            'space_id': space_id,
            'space_title': space.title,
        }
    now = datetime.datetime.now()
    fname = '%s-%s-%s_%s.csv' % (now.year, now.month, now.day, str(uuid.uuid4()))
    path = '_SSL_reports/%s' % space_id
    up_file = UploadedFile.create_in_gcs(path=path, file_name=fname, content_type='text/csv')
    with up_file.gcs_handler('w') as f:
        templates = Content.objects.filter(content_type=ContentType.TEMPLATE, spaces=str(space_id))
        f.write('--Templates--\n')
        fc2, ac2 = _check_contents(templates, f)
        lessons = Content.objects.filter(content_type=ContentType.LESSON, spaces=str(space_id))
        f.write('--Lessons--\n')
        fc1, ac1 = _check_contents(lessons, f)
        all_contents_count = ac1 + ac2
        fixable_contents_count = fc1 + fc2
        f.write('--Summary--\n')
        report_footer = 'Contents need to be fixed per all: <strong>%s / %s</strong>\n' % (fixable_contents_count, all_contents_count)
        report_footer = str(report_footer.encode('utf-8'))
        f.write(report_footer)
        f.close()
        up_file.save()
    log_data['lessons_checked'] = all_contents_count
    log_data['problems_found'] = fixable_contents_count
    if fixable_contents_count == 0:
        logger.info(log_data)
        up_file.delete()
    else:
        log_data['report_url'] = '/%s/%s_%s' % (preview_prefix, space_id, up_file.id)
        log_data['recipients'] = get_users_for_space(space)
        logger.error(log_data)
    return HttpResponse('ok')


def get_users_for_space(space):
    users = []
    for sa in space.spaceaccess_set.filter(is_deleted=False):
        try:
            if sa.user.is_active:
                users.append({
                    'username': sa.user.username,
                    'email': sa.user.email
                })
        except Exception as e:
            logging.error('Space error: %s --> %s' % (space, e))
    return users


@backend
def check_ssl_corporate_spaces(request):
    companies = Space.objects.filter(space_type=SpaceType.CORPORATE, parent=None, is_deleted=False).order_by('title')
    for space in companies:
        trigger_backend_task('/mycontent/check_ssl_space_backend/%s' % space.id, queue_name='localization')
    return HttpResponse('OK')


@backend
def check_ssl_private_spaces(request):
    private_spaces = Space.objects.filter(space_type=SpaceType.PRIVATE, is_deleted=False)
    tasks_urls = []
    for batch in safe_iterate(private_spaces, 50):
        for space in batch:
            if space.parent is not None:
                continue
            try:
                sa = SpaceAccess.objects.filter(space=space)[0]
                if sa.is_deleted:
                    continue
                if not sa.user.is_active:
                    continue
            except Exception as e:
                logging.error('Space error: %s --> %s' % (space, e))
                continue
            tasks_urls.append('/mycontent/check_ssl_space_backend/%s' % space.id)

    trigger_backend_tasks(tasks_urls, target=get_versioned_module('localization'), queue_name='localization', time_delta=0)
    return HttpResponse('OK')


@login_required
@has_space_access(Permission.CONTENT_EDIT_HISTORY)
def set_version(request, content_id, version_id):
    content = Content.get_cached_or_404(content_id)
    user_editing = content.who_is_editing()
    if user_editing is not None:
        messages.warning(request, 'Lesson is currently opened in editor by user <%s>, current version not changed.' % (user_editing))
        return HttpResponseRedirect('/mycontent/%s/history' % (content_id))
    file_storage = FileStorage.objects.get(pk=version_id)
    content.file = file_storage
    content.save()
    metadata_updated.send(sender=None, content_id=content_id)
    # return HttpResponseRedirect('/mycontent/%s/history' % (content_id))
    return HttpResponseRedirect('/mycontent')

@login_required
@has_space_access(Permission.CONTENT_EDIT)
def remove_version(request, content_id, version_id, old_version):
    old_version = FileStorage.objects.get(pk=old_version)
    content = get_content_with_changed_content_file(content_id, old_version)
    file_storage = FileStorage.objects.get(pk=version_id)
    file_storage.delete()
    content.modified_date = datetime.datetime.now()
    content.stop_editing(request.user)
    content.save()
    return get_redirect(request)

# Fix to use in case of DoesNotExist error (FileStorage matching query does not exist)
@login_required
@has_space_access(Permission.CONTENT_EDIT)
def fix_removed_version(request, content_id):
    content = Content.get_cached(id=content_id)
    files = FileStorage.objects.filter(history_for=content).order_by('-version')
    msg='Nothing to do...'
    if files.count():
        file = files[0]
        if content.file_id != file.id:
            content.file = file
            content.save()
            msg='Fixed'
    return HttpResponse(msg)

def go_to_page(request):
    page = request.GET.get("page", 1)
    extra_params = request.GET.get("extra_params", {})
    content_type = request.GET.get("type")
    target = get_redirect_url(request) + "?page=" + page + extra_params + content_type
    return HttpResponseRedirect(target)

@login_required
@has_space_access(Permission.CONTENT_EDIT)
def update_template(request, content_id):
    content = Content.get_cached_or_404(id=content_id)
    is_updated = update_content_template(content, request.user, request.POST.getlist('preferences'))
    if is_updated == UpdateTemplateStatus.UPDATED:
        messages.info(request, 'Template for lesson <%s> has been updated' % content.title)
    elif is_updated == UpdateTemplateStatus.CONTENT_CURRENTLY_EDITED:
        messages.warning(request, 'Lesson <%s> is currently being edited.' % content.title)
    elif is_updated == UpdateTemplateStatus.TEMPLATE_CURRENTLY_EDITED:
        messages.warning(request, 'Template for lesson <%s> is currently being edited.' % content.title)
    else:
        messages.warning(request, 'Lesson <%s> does not have associated template or the template styles are empty' % content.title)
    cache.delete('templates_for_%s' % request.user)
    cache.delete('templates_for_%s' % request.user.company)
    return get_redirect(request)

@login_required
@has_space_access(Permission.ASSET_EDIT)
def update_assets(request, content_id):
    content = Content.get_cached_or_404(id=content_id)
    user = content.who_is_editing()
    confirmed = request.GET.get('confirmed', None)
    if user and not confirmed:
        back = get_redirect_url(request)
        return render(request, 'mycontent/update_assets.html',
                      {
                          'username' : user.username,
                          'back' : back
                      })

    content.set_user_is_editing(request.user)
    messages.info(request, 'Assets for lesson <%s> will be updated in background. You will be notified via email when it is finished.' % content.title)
    trigger_backend_task('/mycontent/update_assets_async/%s/%s' % (content_id, request.user.id), target=get_versioned_module('download'), queue_name='download')
    return get_redirect(request)

@backend
def update_assets_async(request, content_id, user_id):
    try:
        content = Content.get_cached(id=content_id)
        user = User.objects.get(pk=user_id)
        if not verify_content_access(content, user, Permission.ASSET_EDIT):
            send_no_access_notification(user.email, 'You don\'t have rights to update assets')
            return HttpResponse()
        clean_content_assets(user, content)
        send_message(settings.SERVER_EMAIL, [user.email], 'Update assets finished', 'Update assets for content "%s" finished' % content.title)
    except Exception:
        logging.exception("Update assets failed")
        import traceback
        mail_admins("Update assets failed", traceback.format_exc())
        send_message(settings.SERVER_EMAIL, [user.email], 'Update assets failed', 'Please contact administrator.')
    finally:
        content.stop_editing(user)
    return HttpResponse()

@login_required
@has_space_access(Permission.CONTENT_EDIT)
def extract_pages(request, content_id, space_id=None):
    content = Content.get_cached_or_404(id=content_id)
    parsed = parser.parse(request.POST.urlencode())
    pages_to_extract = []
    if 'pages' in parsed:
        pages_to_extract = list(parsed['pages'].keys())
    if not pages_to_extract:
        messages.warning(request, 'You need to select some pages to extract new lesson')
        return get_redirect(request)
    new_content = content.makeCopy(True, request.user, pages_to_extract)
    new_content.title = "Subset of %s" % content.title
    new_content.save()
    if space_id is not None:
        space = get_object_or_404(Space, pk=space_id)
    else:
        space = get_private_space_for_user(request.user)
    add_content_to_space(new_content, space, False)
    messages.info(request, 'New lesson has been created based on selected pages')
    return get_redirect(request)


@backend
@login_required
@user_passes_test(lambda user: user.is_superuser)
def fix_being_edited(request):
    max_date = datetime.date.today() - datetime.timedelta(14)
    old_cus = CurrentlyEditing.objects.filter(edited_since__lt=max_date)
    ret = '<h1>Fix</h1> <p>Entries to delete: %s</p>' % old_cus.count()
    i = 0
    try:
        while old_cus.count():
            for cu in old_cus[:100]:
                cu.delete()
                i+=1
    except DeadlineExceededError:
        ret = "%s<br><strong>Max time Exception</strong>" % ret
    finally:
        ret = "%s<br>Deleted rows: %s" % (ret, i)
    return HttpResponse(ret)


def broken_entry_list(lesson, file_id, doc, entry):
    return '%s/corporate/view/%s - %s (tpl_id=%s)' % (settings.BASE_URL, lesson.id, lesson, file_id)


def search_broken_lessons(space_id, broken_entry_method):
    import xml.parsers.expat
    lessons = list(Content.objects.filter(spaces=str(space_id)).values('id'))
    resp_log = ''
    i = 0
    for l_id in lessons:
        l = Content.get_cached(id=l_id['id'])
        try:
            doc = xml.dom.minidom.parseString(l.file.contents)
            entry = None
            for e in doc.getElementsByTagName('entry'):
                if e.getAttribute('key') == 'theme.href':
                    entry = e
                    break
            if not entry:
                continue

            value = entry.getAttribute('value')
            if value == '':
                continue

            splitted_value = value.split('/')
            if len(splitted_value) != 3:
                continue

            file_id = int(splitted_value[2])
            fses = FileStorage.objects.filter(pk = file_id)
            if len(fses):
                continue

            i += 1
            resp_log += '\n%s. ' % i
            resp_log += broken_entry_method(l, file_id, doc, entry)
        except xml.parsers.expat.ExpatError:
            continue
    return resp_log


@login_required
@user_passes_test(lambda user: user.is_superuser)
def broken_templates_trigger(request):
    r = ''
    i = 0
    companies = Space.objects.filter(space_type=SpaceType.CORPORATE, parent=None, is_deleted=False).order_by('title')
    for space in companies:
        i += 1
        r += '%s. %s\n' % (i, space)
        trigger_backend_task('/mycontent/broken_templates/%s/%s' % (space.id, request.user.id), target=get_versioned_module('backup'), queue_name='backup')
    return HttpResponse(r, content_type='text/plain')


@backend
def broken_templates(request, space_id, user_id):
    company = Space.objects.get(pk=space_id)
    subject = 'Lessons with broken templates for company %s '% company
    user = User.objects.get(pk=user_id)
    resp_log = 'The following lessons has broken templates:<br />\n'
    resp_log += search_broken_lessons(space_id, broken_entry_list).replace('\n', '<br />\n')
    send_message(settings.SERVER_EMAIL, [user.email], subject, resp_log)
    return HttpResponse('OK')


class ConfirmSelfEditing(LoginRequiredMixin, HasSpacePermissionMixin, TemplateView):

    permission = Permission.CONTENT_VIEW

    def get(self, request, *args, **kwargs):
        back = request.REQUEST.get("back_url") or get_redirect_url(request)
        full_path_to_editor = set_new_token_and_return_path(request)

        return render(request, 'mycontent/confirm_self_edit_content.html',
                      {
                          'back': back,
                          'full_path_to_editor': full_path_to_editor,
                      })


class ConfirmSelfEditingAddon(LoginRequiredMixin, HasSpacePermissionMixin, TemplateView):

    permission = Permission.CONTENT_EDIT

    def get(self, request, *args, **kwargs):
        back = request.REQUEST.get("back_url") or get_redirect_url(request)
        full_path_to_editor = set_new_token_and_return_path(request)

        return render(request, 'mycontent/confirm_self_edit_content_addon.html',
                      {
                          'back': back,
                          'full_path_to_editor': full_path_to_editor,
                      })


class ConfirmEditing(LoginRequiredMixin, HasSpacePermissionMixin, TemplateView):

    permission = Permission.CONTENT_EDIT

    def get(self, request, *args, **kwargs):
        who_editing = request.REQUEST.get("who")
        back = request.REQUEST.get("back_url") or get_redirect_url(request)
        full_path_to_editor = set_new_token_and_return_path(request)

        return render(request, 'mycontent/confirm_edit_content.html',
                      {
                          'back': back,
                          'full_path_to_editor': full_path_to_editor,
                          'who_editing': who_editing
                      })
