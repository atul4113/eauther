from django.core.exceptions import PermissionDenied
from django.utils.translation import get_language_info
from django.shortcuts import render, get_object_or_404
from django.views.generic import View, TemplateView
from lorepo.corporate.decorators import HasSpacePermissionMixin
from lorepo.filestorage.models import FileStorage
from lorepo.spaces.models import Space, SpaceAccess, SpaceType, UserSpacePermissions
from lorepo.mycontent.util import get_content_details,\
    get_addon_source_code, get_recently_opened
from lorepo.mycontent.models import ContentType, Content,\
    SpaceTemplate
from lorepo.spaces.util import get_spaces_for_copy, \
    get_space_for_content, get_contents_and_total, \
    get_spaces_subtree, change_contentspace, \
    get_corporate_spaces_for_user, get_private_space_for_user, \
    _get_subspaces, get_spaces_tree, load_kids, \
    get_locked_companies, get_projects_with_publications, is_company_locked
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from lorepo.filestorage.forms import UploadForm
from lorepo.corporate.models import CorporateLogo, CorporatePublicSpace,\
    CompanyProperties, PROJECT_ADMIN_PERMISSIONS, SpaceJob, JOB_TYPE, DemoAccountLessons
from google.appengine.api import blobstore
from lorepo.corporate.utils import set_uploaded_file, is_in_public_category,\
    get_spaces_path_for_corporate_content, get_contents,\
    get_publication_for_space, get_division_for_space,\
    check_manage_access_rights, get_space_accesses_to_projects
from lorepo.spaces.form import SpaceForm
from django.contrib.auth.models import User
from django.core.paginator import Paginator
import datetime
from lorepo.mycontent.forms import ContentMetadataForm, AddonMetadataForm
from lorepo.corporate.forms import CreateCompanyForm, CopyToAccount, CreateOwnerCompanyForm
import re
from lorepo.token.decorators import token, TokenMixin
from lorepo.spaces.service import update_space, insert_space
from lorepo.mycontent.service import add_content_to_space,\
    remove_content_space, update_content_space
from libraries.utility.redirect import get_redirect, get_redirect_url
from lorepo.corporate.signals import company_structure_changed,\
     kids_for_space_changed, access_rights_changed, user_spaces_flush
from django.contrib import messages
from mauthor.bug_track.forms import AddBugForm
from mauthor.bug_track.models import Bug
from mauthor.bug_track.util import get_users_for_email, get_last_bug_for_content
from mauthor.bug_track.views import add_bug
import libraries.utility.cacheproxy as cache
from mauthor.company.util import remove_spaceaccesses
from mauthor.states.util import get_current_state_for_content
import logging
from libraries.utility.cacheproxy import delete_template_fragment_cache
from lorepo.permission.decorators import has_space_access
from lorepo.permission.models import Permission, Role
from lorepo.permission.util import create_company_user, check_space_access
from libraries.utility.helpers import get_values_per_page, get_object_or_none
from libraries.utility.environment import get_versioned_module
from libraries.utility.queues import trigger_backend_task
from django.core.mail import mail_admins
from logging import info
from lorepo.mycontent.signals import addon_deleted, addon_published,\
    metadata_updated
from django.template.context import Context
from django.template.loader import get_template, render_to_string
from mauthor.metadata.util import save_metadata_from_request, update_page_metadata, toggle_page_metadata,\
    get_metadata_values_and_definitions, copy_metadata
from libraries.core.paginator import CustomPaginator
from lorepo.mycontent.decorators import is_being_edited
from libraries.utility.decorators import backend, BackendMixin
from lorepo.filestorage.utils import create_new_version
from django.views.decorators.http import require_POST
from lorepo.public.util import send_message
from mauthor.utility.decorators import LoginRequiredMixin
from lorepo.token.models import TOKEN_KEYS
from lorepo.token.util import create_publication_action_token, create_mycontent_editor_token, create_mycontent_edit_addon_token
import settings
from django.core.mail import send_mail
import libraries.utility.queues


@login_required
@has_space_access(Permission.CONTENT_VIEW)
def view(request, content_id):
    context = {}
    content = Content.get_cached_or_404(id=content_id)
    context['content'] = content
    if request.user.is_authenticated():
        context['divisions'] = get_spaces_for_copy(request.user)
    else:
        context['divisions'] = []

    context['spaces'] = get_spaces_path_for_corporate_content(context['content'], lambda space: space.is_corporate())
    context['tl_space'] = top_level_space = get_space_for_content(context['content'])

    if request.method == 'POST':
        context['form'] = add_bug(request, content.id)
        context['back_url'] = context['form'].data['next']
        return HttpResponseRedirect('/corporate/view/%s?next=%s' % (content.id, context['back_url']))
    else:
        context['form'] = AddBugForm()
        context['back_url'] = get_redirect_url(request, target='/corporate/list/%s' % top_level_space.id)

    space = get_space_for_content(content)
    usp = UserSpacePermissions.get_cached_usp_for_user(request.user)
    context['is_owner'] = request.user.is_superuser or usp.has_owner_role_for_space(space.id)
    context['bugs'] = Bug.objects.filter(content=content).order_by('-created_date')
    context['users'] = get_users_for_email(space)
    user_permissions = Permission().get_all() if request.user.is_superuser else usp.get_permissions_for_space(space.id)
    if not user_permissions:
        user_permissions = []
    context['user_permissions'] = user_permissions
    context['has_more_actions_permissions'] = request.user.is_superuser or _has_more_actions_permissions(user_permissions)
    context['Permission'] = Permission
    context['copy_spaces'] = get_spaces_for_copy(request.user)
    token, token_key = create_mycontent_editor_token(request.user)
    context['sub_menus'] = _get_view_sub_menus(user_permissions, content, top_level_space, '/corporate/view/%s' % content_id, token, token_key)
    context['is_company_locked'] = is_company_locked(request.user.company)
    context['token'] = token
    context['token_key'] = token_key

    state, is_current = get_current_state_for_content(content)
    if state:
        if is_current:
            context['state'] = '%s (In Progress)' % state.name
        else:
            context['state'] = '%s (Ready)' % state.name

    return render(request, 'corporate/view.html', context)


def _get_view_sub_menus(user_permissions, content, top_level_space, back_url, token, token_key=None):
    sub_menus = []

    if Permission.CONTENT_EDIT in user_permissions:
        sub_menus.append(('Edit Lesson', '/mycontent/%s/editor?next=%s&%s=%s' % (content.id, back_url, token_key, token), None))

    if Permission.CONTENT_EDIT_METADATA in user_permissions:
        sub_menus.append(('Edit Metadata', '/corporate/%s/metadata?next=%s' % (content.id, back_url), None))

        if content.enable_page_metadata:
            sub_menus.append(('Edit Page Metadata', '/mycontent/%s/pagemetadata?next=%s' % (content.id, back_url), None))

    if Permission.CONTENT_MAKE_PUBLIC in user_permissions:
        if content.is_content_public():
            sub_menus.append(('Unpublish', '/corporate/%s/makepublic?next=%s' % (content.id, back_url), None))
        else:
            sub_menus.append(('Publish', '/corporate/%s/makepublic?next=%s' % (content.id, back_url), None))

    if Permission.CONTENT_REMOVE in user_permissions:
        sub_menus.append(('Delete Lesson', '/corporate/%s/delete?next=/corporate/list/%s' % (content.id, top_level_space.id), {
            'is_delete': True
        }))

    return sub_menus


@login_required
@has_space_access(Permission.CONTENT_VIEW)
def view_addon(request, addon_id):
    context = get_content_details(request, addon_id, ContentType.ADDON)

    if request.user.is_authenticated():
        context['divisions'] = get_spaces_for_copy(request.user)
    else:
        context['divisions'] = []

    context['spaces'] = get_spaces_path_for_corporate_content(context['content'], lambda space: space.is_corporate())
    context['addon'] = context['content']
    context['tl_space'] = get_space_for_content(context['content'])
    context['private_space'] = get_private_space_for_user(request.user)
    addon_source = get_addon_source_code(context['addon'].file.contents)
    context.update(addon_source)
    
    return render(request, 'corporate/view_addon.html', context)

@login_required
@has_space_access(Permission.CORPORATE_UPLOAD_LOGO, True)
def upload(request):
    """
    Handler wywolywany po uploadzie obrazka dla CorporateLogo
    """
    space = request.user.company
        
    corporate_logo_list = CorporateLogo.objects.filter(space=space)
        
    if request.method == 'POST':
        if len(request.FILES) > 0:
            form = UploadForm(request.POST, request.FILES)
            uploaded_file = form.save(False)
            uploaded_file.filename = request.FILES['file'].name
            set_uploaded_file(uploaded_file, request.user, corporate_logo_list, space, request.FILES['file'].content_type)
            return HttpResponseRedirect('/corporate/upload')
        else:
            return HttpResponseRedirect('/corporate/upload')
    else:
        upload_url = blobstore.create_upload_url('/corporate/upload')
        form = UploadForm()
        return render(request, 'corporate/upload.html', {
            'upload_url': upload_url,
            'form': form,
        })

@login_required
@has_space_access(Permission.SPACE_EDIT, True)
def company_public_spaces(request):
    spaces = request.user.public_category.kids.all()
    company_structure_changed.send(None, company_id=request.user.company.id, user_id=request.user.id)
    return render(request, 'corporate/public.html', {'spaces' : spaces, 'company' : request.user.company})

@login_required
@has_space_access(Permission.SPACE_EDIT, True)
def add_public_space(request):
    if request.method == 'POST':
        form = SpaceForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            space = Space(title=title, space_type=SpaceType.PUBLIC)
            space.parent = request.user.public_category
            space.top_level = request.user.public_category
            insert_space(space)

    return HttpResponseRedirect('/corporate/publicspaces')

@login_required
@has_space_access(Permission.SPACE_EDIT, True)
def company_divisions(request):
    divisions = request.user.company.kids.all().order_by('title')
    return render(request, 'corporate/divisions.html', {'divisions' : divisions, 'company' : request.user.company})

@login_required
@has_space_access(Permission.SPACE_EDIT)
def rename_division(request, space_id):
    space = get_object_or_404(Space, id=space_id)
    if request.method == 'POST':
        form = SpaceForm(request.POST)
        if form.is_valid():
            space.title = form.cleaned_data['title']
            update_space(space, propagate_update=False) #update propagation would trigger recalculation of access rights for the whole company
            company_structure_changed.send(None, company_id=space.top_level.id, user_id=request.user.id)
            return HttpResponseRedirect('/corporate/divisions')
    return render(request, 'corporate/rename_project.html', {'space' : space})

@login_required
@has_space_access(Permission.SPACE_EDIT)
def delete_division(request, space_id):
    space = get_object_or_404(Space, pk=space_id)
    remove_spaceaccesses(space)
    company = space.top_level
    space.parent = None
    space.top_level = None
    space.is_deleted = True
    update_space(space)
    trigger_backend_task('/corporate/remove_contents/%s' % space_id, target=get_versioned_module('download'), queue_name='default')
    logging.info('Project %s has been removed from company %s [user who executed this action: %s]', space, company, request.user)
    company_structure_changed.send(None, company_id=company.id, user_id=request.user.id)
    messages.info(request, 'Project <%s> successfully deleted' % space.title)
    return get_redirect(request, '/corporate/divisions')

@backend
def remove_contents_from_division(request, space_id):
    space = Space.objects.get(pk=space_id)
    contents = get_contents(space)
    for content in contents:
        content.is_deleted = True
        content.save()
        metadata_updated.send(sender=None, content_id=content.id)
    return HttpResponse('OK')

@login_required
@has_space_access(Permission.SPACE_EDIT)
def add_division(request, space_id):
    if request.method == 'POST':
        form = SpaceForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            parent = Space.objects.get(pk=space_id)
            space = Space(title=title, parent=parent, space_type=parent.space_type)
            insert_space(space)
            messages.info(request, "Changes to the access rights in your company structure will be propagated in the background. This process can take up to a few minutes.")
            kids_for_space_changed.send(None, space_id=space_id)
            company_structure_changed.send(None, company_id=space.top_level.id, user_id=request.user.id)
    return HttpResponseRedirect('/corporate/divisions')

@login_required
@has_space_access(Permission.CORPORATE_VIEW_PANEL, True)
def admin_panel(request):
    return render(request, 'corporate/admin.html')


def _check_project_admin_permissions(request):
    has_permission = False
    for sa in request.user.spaceaccess_set.all():
        if sa.space.is_private():
            continue
        for permission in PROJECT_ADMIN_PERMISSIONS:
            if sa.has_permission(permission):
                has_permission = True
    if not has_permission:
        raise PermissionDenied

def _check_company_admin(space_accesses):
    for sa in space_accesses:
        if sa.space.is_company():
            return True
    return False

@login_required
def division_panel(request):
    _check_project_admin_permissions(request)
    params = {
        'has_manage_access_rights': check_manage_access_rights(request.user.spaceaccess_set.all()),
        'space_accesses': get_space_accesses_to_projects(request.user.spaceaccess_set.all()),
        'is_company_admin': _check_company_admin(request.user.spaceaccess_set.all())
    }
    return render(request, 'corporate/division_admin.html', params)

@login_required
def public_space(request, space_id):
    if space_id is None:
        space_request = request.user.public_category.kids.all()[0]
    else:
        space_id = int(space_id)
        space_request = Space.objects.get(id=space_id)

    spaces = request.user.public_category.kids.all()
    subspaces = _get_subspaces([space_request])
    subspaces.add(space_request)

    content_list = []
    total = get_contents_and_total(spaces, subspaces, content_list)

    path_spaces = [space_request]
    path_space = space_request
    while path_space.top_level != path_space.parent:
        path_space = path_space.parent
        path_spaces.append(path_space)
    path_spaces.reverse()

    paginator = Paginator(content_list, 10)
    page_number = request.GET.get('page')
    if page_number != None:
        page_content = paginator.page(page_number)
    else:
        page_content = paginator.page(1)

    return render(request, 'corporate/public_spaces.html', 
                  {'contents'       : page_content.object_list, 
                   'paginator'      : paginator,
                   'current_page'   : page_content,
                   'spaces'         : sorted(list(spaces), key=lambda space: space.rank),
                   'space_request'  : space_request,
                   'total'          : total,
                   'path_spaces'    : path_spaces,
                   })

def trash(request, space_id=None):
    return _index(request, space_id, is_trash=True)

def list_presentations(request, space_id=None):
    return _index(request, space_id, is_trash = False)

def _get_user_sub_menus(user_permissions, space_id, publication_id, project_id = None, is_super_user=False):
    sub_menus = []
    if (Permission.CONTENT_EDIT in user_permissions):
        sub_menus.append(('Create Lesson', '/mycontent/addcontent/%(space_id)s?next=/corporate/list/%(space_id)s' % { 'space_id' : space_id }))
        sub_menus.append(('Create Addon', '/mycontent/addon/%(space_id)s?next=/corporate/list/%(space_id)s' % { 'space_id' : space_id }))
    if (Permission.EXCHANGE_IMPORT in user_permissions):
        sub_menus.append(('Import Lesson', '/exchange/import/%(space_id)s?next=/corporate/list/%(space_id)s' % { 'space_id' : space_id }))
    if (Permission.LOCALIZATION_IMPORT in user_permissions):
        sub_menus.append(('Import XLIFF', '/localization/create_import/%(space_id)s?next=/corporate/list/%(space_id)s' % { 'space_id' : space_id }))

    sub_menus.append(('Import InDesign XML (Beta)', '/indesign/upload/%(space_id)s?next=/corporate/list/%(space_id)s' % { 'space_id' : space_id }))
    sub_menus.append(('Show Kanban', '/states/show_kanban/%(publication_id)s?next=/corporate/list/%(publication_id)s' % { 'publication_id' : publication_id }))

    if (Permission.COURSE_MANAGE in user_permissions):
        sub_menus.append(('Manage Courses', '/course/list/%(project_id)s' % { 'project_id' : project_id }))

    if is_super_user:
        sub_menus.append(('Property change', '/lessons_parsers/change_properties/%(space_id)s' % {'space_id': space_id}))
        sub_menus.append(('Remove unused descriptors', '/lessons_parsers/remove_descriptors/%(space_id)s' % {'space_id': space_id}))

    return sub_menus

def _has_more_actions_permissions(user_permissions):
    for perm in Permission().get_more_actions_permissions():
        if perm in user_permissions:
            return True
    return False

@login_required
@has_space_access(Permission.CONTENT_VIEW)
def _index(request, space_id=None, is_trash=False):
    if space_id is None:
        raise Http404
    else:
        space_id = int(space_id)
        requested_space = Space.objects.get(id=space_id)

    division = requested_space
    while not division.is_second_level():
        division = division.parent

    spaces = division.kids.filter(is_deleted=False)
    usp = UserSpacePermissions.get_cached_usp_for_user(request.user)
    if not request.user.is_superuser:
        spaces = [space for space in spaces if usp.get_permissions_for_space(space.id)]
    load_kids(spaces)
    spaces = sorted(list(spaces), key=lambda space: space.title)

    if not is_trash:
        if requested_space.is_second_level() and len(spaces) > 0:
            if 'last_project_id' in request.session:
                if division.id in request.session['last_project_id']:
                    space_id = request.session['last_project_id'][division.id]
                else:
                    space_id = spaces[0].id
                    request.session['last_project_id'][division.id] = space_id
            else:
                space_id = spaces[0].id
                request.session['last_project_id'] = { division.id : space_id }
        else:
            if 'last_project_id' in request.session and space_id != division.id:
                request.session['last_project_id'][division.id] = space_id

    request.session.save()

    header = division.title
    spaces_list = Space.objects.filter(id=space_id)
    if len(spaces_list) > 0:
        requested_space = spaces_list[0]

    # Read publication
    publication = requested_space
    while publication.parent and not publication.parent.is_second_level():
        publication = publication.parent

    subheader = None
    if not requested_space.is_second_level() and not is_trash:
        subheader = requested_space.title

    set_order_by_cookie = False
    order_by = request.GET.get('order_by')
    if order_by not in ['title', '-title', 'modified_date', '-modified_date']:
        order_by = request.COOKIES.get('corporate_list_order_by','-modified_date')
    else:
        set_order_by_cookie = True
    content_list = get_contents(requested_space, is_trash, order_by)
    
    page_number = int(request.GET.get('page')) if 'page' in request.GET and re.search("^[\d]+$", request.GET.get('page')) else 0
    paginator = CustomPaginator(content_list, 10)
    page_content = paginator.page(page_number)
    
    page_contents = []
    for item in page_content.object_list:
        state, is_current = get_current_state_for_content(item)
        if state:
            if is_current:
                item.state = '%s (In Progress)' % state.name
            else:
                item.state = '%s (Ready)' % state.name

        item.last_bug = get_last_bug_for_content(item)
        page_contents.append(item)

    user_permissions = Permission().get_all() if request.user.is_superuser else usp.get_permissions_for_space(requested_space.id)
    if not user_permissions:
        user_permissions = []

    sub_menus = _get_user_sub_menus(user_permissions, space_id, publication.id, division.id, request.user.is_superuser)

    editor_token, editor_token_key = create_mycontent_editor_token(request.user)
    addon_token, addon_token_key = create_mycontent_edit_addon_token(request.user)
    response = render(request, 'corporate/list.html',
                      {
                          'contents': page_contents,
                          'paginator': paginator,
                          'spaces': sorted(spaces, key=lambda space: space.rank),
                          'divisions': sorted(list(request.user.divisions.values()), key=lambda space: space.title),
                          'private_space': get_private_space_for_user(request.user),
                          'space_request': requested_space,
                          'is_trash': is_trash,
                          'header': header,
                          'subheader': subheader,
                          'current_page': page_content,
                          'division': division,
                          'user_permissions': user_permissions,
                          'Permission': Permission,
                          'has_more_actions_permissions': request.user.is_superuser or _has_more_actions_permissions(user_permissions),
                          'editor_token': editor_token,
                          'editor_token_key': editor_token_key,
                          'addon_token': addon_token,
                          'addon_token_key': addon_token_key,
                          'sub_menus': sub_menus,
                          'extra_params': {'order_by': order_by},
                          'is_company_locked': is_company_locked(request.user.company)
                      })
    if set_order_by_cookie:
        response.set_cookie('corporate_list_order_by',value=order_by, max_age=60*60*24*30)
    return response

@login_required
@has_space_access(Permission.CONTENT_REMOVE)
def delete(request, content_id):
    now = datetime.datetime.now()
    content = Content.get_cached_or_404(id=content_id)
    content_space = [content_space for content_space in content.contentspace_set.all() if not content_space.space.is_public()][0]
    url = '/corporate/list/%(space_id)s' % {'space_id' : content_space.space.id }
    content_space.is_deleted = not content_space.is_deleted
    update_content_space(content_space)
    content.public_version = None
    content.modified_date = now
    content.is_deleted = not content.is_deleted
    content.save()
    metadata_updated.send(sender=None, content_id=content_id)

    if content.content_type == ContentType.ADDON:
        addon_deleted.send(sender=None, company_id=request.user.company.id)

    return get_redirect(request, url)

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
            content.modified_date = datetime.datetime.now()
            content.add_title_to_xml()
            content.set_score_type(form.cleaned_data['score_type'])
            content.save()

            try:
                space_id = int(form.data['space_id'])
            except ValueError:
                space_id = 0 #not change space if is empty

            if space_id != 0:
                change_contentspace(content, space_id, False)
            cache.delete('templates_for_%s' % (request.user.company.id))

            save_metadata_from_request(request, content)
            metadata_updated.send(sender=None, content_id=content.pk)

            messages.success(request, 'Metadata successfully saved')
            return HttpResponseRedirect(form.data['next'])
        else:
            space_id = int(form.data["space_id"])
            if space_id != 0:
                assigned_space = Space.objects.get(pk=space_id)
    else:
        form = ContentMetadataForm()
        form.initialize(content)

    next_url = request.GET.get("next") if request.GET.get("next") else form.data['next']

    assigned_project = get_division_for_space(assigned_space)
    assigned_publication = get_publication_for_space(assigned_space)
    if not assigned_space.is_company() and not assigned_space.is_project() and not assigned_space.is_publication():
        assigned_unit = assigned_space
    else:
        assigned_unit = None

    metadata_values = get_metadata_values_and_definitions(content, request.user.company)
    #user should be able to set the project to the current value or one of the projects that he is assigned to
    divisions = list(set([assigned_project] + list(request.user.divisions.values())))

    return render(request, 'corporate/metadata.html', 
                  { 
                    'content'               : content,
                    'assigned_unit'         : assigned_unit, 
                    'form'                  : form,
                    'next'                  : next_url,
                    'is_template'           : is_template,
                    'projects'              : divisions,
                    'assigned_project'      : assigned_project,
                    'assigned_publication'  : assigned_publication,
                    'assigned_space'        : assigned_space,
                    'definitions'           : metadata_values,
                    'content_id'            : str(content.id),
                    'language_bidi'         : language_bidi
                    })

@require_POST
@login_required
@has_space_access(Permission.CONTENT_MAKE_PUBLIC)
def publish(request, content_id):
    content = Content.get_cached_or_404(id=content_id)
    
    content.is_public = True
    content.public_version = content.file

    content.save()
    
    if content.content_type == ContentType.ADDON:
        addon_published.send(sender=None, company_id=request.user.company.id)
    
    return HttpResponse()

@require_POST
@login_required
@has_space_access(Permission.CONTENT_EDIT)
def create_new_content_version(request, content_id):
    content = Content.get_cached_or_404(id=content_id)
    content.file = create_new_version(content.file, request.user, True)
    if content.file.history_for is None:
        content.file.history_for = content
        content.file.save()
    content.save()
    
    return HttpResponse('/file/%s' % content.file.id)

@login_required
def get_publications_for_project_json(request):
    project = get_object_or_none(Space, pk = request.GET['projectId'])
    publications = [] if project == None else [space for space in get_spaces_subtree(project.id) if space.parent.is_second_level()]
    context = Context({ 'publications' : publications })
    template = get_template('corporate/get_publications_for_project.json')
    rendered = template.render(context)
    return HttpResponse(rendered)

@login_required
def select_unit(request, content_id, publication_id):
    content = Content.get_cached_or_404(id = content_id)
    publication = get_object_or_404(Space, pk = publication_id)
    units = [unit for unit in publication.kids.filter(is_deleted = False) if check_space_access(unit, request.user, Permission.CONTENT_EDIT_METADATA)]

    return HttpResponse(
                render_to_string('corporate/select_unit.html', {
                      'content' : content,
                      'publication' : publication,
                      'units' : sorted(units, key=lambda unit: unit.rank),
                      'request' : request,
                      'currentlySelected' : get_space_for_content(content)
                  })
            )

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
    return render(request, 'corporate/metadata_addon.html',
                  {
                   'form' : form, 
                   'addon' : addon, 
                   'next' : next_url,
                   })


@login_required
@user_passes_test(lambda user: user.is_superuser)
def create_company(request):

    if request.method == 'POST':
        form = CreateCompanyForm(request.POST)
        if form.is_valid():
            user = User.objects.get(username = form.cleaned_data['user'])
            space = Space(title = form.cleaned_data['space'], space_type = 3)
            insert_space(space)
            space_public = Space(title = space.title + ' Public', space_type = 2)
            insert_space(space_public)
            role = Role(name = 'owner', permissions = Permission().get_all(), company = space)
            role.save()
            space_access = SpaceAccess(user=user, space=space, roles = [role.pk])
            space_access.save()
            create_company_user(space, user)
            cps = CorporatePublicSpace(company = space, public_category = space_public)
            cps.save()
            properties = CompanyProperties(company = space)
            if form.cleaned_data['valid_until']:
                properties.valid_until = form.cleaned_data['valid_until']
            if form.cleaned_data['max_accounts']:
                properties.max_accounts = form.cleaned_data['max_accounts']
            properties.save()
            messages.info(request, 'Company <%s> created and user <%s> is an owner' % (space.title, user.username))
            delete_template_fragment_cache('menu', user)
            return HttpResponseRedirect('/corporate/create_company')
    else:
        form = CreateCompanyForm()
    return render(request, 'corporate/create_company.html', {
                   'form' : form,
                   })

@login_required
@user_passes_test(lambda user: user.is_superuser)
def create_company_owner(request):
    if not request.user.is_superuser:
        raise Http404

    if request.method == 'POST':
        form = CreateOwnerCompanyForm(request.POST)
        if form.is_valid():
            user = User.objects.get(username = form.cleaned_data['user'])
            space = Space.objects.get(pk = form.cleaned_data['space_id'])
            role = Role.objects.get(name = 'owner', company = space)
            space_access = SpaceAccess(user=user, space=space, roles = [role.pk])
            space_access.save()
            create_company_user(space, user)
            messages.info(request, 'Company <%s> has a new owner,  user <%s>' % (space.title, user.username))
            company_structure_changed.send(None, company_id=request.user.company.id, user_id=request.user.id)
            access_rights_changed.send(request.user, user_id=user.id)
            delete_template_fragment_cache('menu', user)
            return HttpResponseRedirect('/corporate/create_company_owner')
    else:
        form = CreateOwnerCompanyForm()
    return render(request, 'corporate/create_company_owner.html', {
                   'form' : form,
                   })

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
        content.is_public = True
        content.public_version = content.file
    else:
        content.is_public = False
        content.public_version = None

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
@user_passes_test(lambda user: user.is_superuser)
def fixdb_public_content_metadata(request):
    for n in range(0, 5):
        trigger_backend_task('/corporate/fixdb_public_content_metadata_task/%s' % n,
                                 target=get_versioned_module('download'),
                                 queue_name='download')
    
    mail_admins('FixDB for public content metadata started', 'FixDB for public content metadata started\nAfter it finished you will be notified via email.')
    
    return HttpResponseRedirect('/user/settings')

@backend
def fixdb_public_content_metadata_task(request, portion):
    portion = int(portion)
    count = Content.objects.count()
    portion_count = count / 5
    offset = portion_count * portion
    counter = 0
    mail_content = 'Content to be fixed:\n'
    
    for n in range(0, portion_count/30 + 1):
        info('Checking content package from %s to %s', str(offset + n*30), str(offset + (n+1)*30))
        contents = Content.objects.all()[offset + n*30:offset + (n+1)*30]
        
        for content in contents:
            if (content.is_public and not content.public_version) or (not content.is_public and content.public_version):
                content_description = 'Name: %s (ID: %s, URL: %s/mycontent/view/%s)\n' % (settings.BASE_URL, content.title, content.id, content.id)
                info('-'*60)
                info('Task #%s: %s' % (str(portion), content))
                mail_content += content_description
                counter += 1
    
    if counter:
        mail_content = 'Task #%s: Found %s content to be fixed!\n%s' % (str(portion), counter, mail_content)
    else:
        mail_content = 'Task #%s: No content found for fix! :)' % str(portion)

    mail_admins('FixDB for public content metadata done with task #%s' % str(portion), mail_content)
    
    return HttpResponse('OK')

@login_required
def fixdb_public_content(request):
    public_contents = Content.objects.filter(is_public=True)
    for content in public_contents:
        spaces = get_corporate_spaces_for_user(content.author)
        if spaces:
            cps = CorporatePublicSpace.objects.filter(company=spaces.pop().top_level)
            if cps:
                public_category = cps[0].public_category
                if not is_in_public_category(content, public_category):
                    add_content_to_space(content, public_category)
    return HttpResponseRedirect('/user/settings')

@login_required
def fixdb_projects(request):
    spaces = Space.objects.all()
    divisions = [space for space in spaces if space.is_second_level() and space.space_type == SpaceType.CORPORATE]
    for div in divisions:
        space = Space(title="Sample project", parent=div)
        insert_space(space)
        for cs in div.contentspace_set.all():
            add_content_to_space(cs.content, space)
            remove_content_space(cs)
    return HttpResponseRedirect('/user/settings')


class JobView(LoginRequiredMixin, TokenMixin, HasSpacePermissionMixin, View):
    # abstract class
    Task = SpaceJob
    token_key = TOKEN_KEYS.PUBLICATION_ACTION
    permission = Permission.SPACE_REMOVE
    job_type = None

    backend_task_url = '/corporate/job/{0}' # {0} - task pk
    success_msg = 'Job created for background work'
    failure_msg = 'Job is already in progress'

    def dispatch(self, request, *args, **kwargs):
        if self.Task.is_any_job_in_progress(kwargs["space_id"]):
            messages.info(request, self.failure_msg)
            return HttpResponseRedirect(request.GET.get('next'))
        else:
            return super(JobView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        task = self.Task(
            space_id=self.kwargs["space_id"],
            created_by=self.request.user,
            job_type=self.job_type
        )

        task.save()

        url = self.backend_task_url.format(task.pk)
        trigger_backend_task(url, target=get_versioned_module('download'), queue_name='download', countdown=5)

        messages.info(self.request, self.success_msg)
        return HttpResponseRedirect(self.request.GET.get('next'))


class SpaceArchiveJobView(JobView):
    job_type = JOB_TYPE.ARCHIVE
    backend_task_url = '/corporate/archive_project_async/{0}'
    success_msg = 'Archiving will be done in background. You will receive email when work will be finished.'
    failure_msg = 'Archiving is already in progress.'


class SpaceRetrieveJobView(JobView):
    job_type = JOB_TYPE.RETRIEVE
    backend_task_url = '/corporate/retrieve_project_async/{0}'
    success_msg = 'Retrieving will be done in background. You will receive email when work will be finished.'
    failure_msg = 'Retrieving is already in progress.'


class SpaceDeleteJobView(JobView):
    job_type = JOB_TYPE.DELETE
    backend_task_url = '/corporate/delete_project_async/{0}'
    success_msg = 'Deleting will be done in background. You will receive email when work will be finished.'
    failure_msg = 'Deleting is already in progress.'


class AbstractJobAsync(BackendMixin, View):
    model = SpaceJob
    success_subject = 'Job executed.'
    success_message = 'Job succesfully finished.'
    failure_message = 'Job failure.'
    failure_subject = 'Job failure'
    admin_mail_title = 'Job project async failed'
    is_deleted = False

    def post(self, request, *args, **kwargs):
        try:
            self.job = get_object_or_404(self.model, pk=kwargs["job_id"])
            self.space = self.job.space
            if self.job.is_not_started():
                self.job.set_status_in_progress()
                self.job.save()
                self.execute()
                self.job.set_status_done()
                self.send_mail_to_user(self.success_subject, self.success_message)
            else:
                return HttpResponse("")

            self.job.save()
        except Exception as e:
            self.job_failure(e)

        return HttpResponse("")

    def job_failure(self, exception):
        import traceback
        self.job.set_status_failed()
        self.job.traceback = traceback.format_exc()
        self.job.save()
        mail_admins(self.admin_mail_title, traceback.format_exc())
        self.send_mail_to_user(self.failure_subject, self.failure_message)

    def send_mail_to_user(self, subject, body):
        send_message(settings.SERVER_EMAIL, [self.job.created_by.email], subject, body.format(self.space))

    def execute(self):
        publication = self.space
        while not publication.parent.is_second_level():
            publication = publication.parent

        if self.space == publication:
            space_accesses = SpaceAccess.objects.filter(space=self.space)
            self.space.is_deleted = self.is_deleted
            update_space(self.space)
            for sa in space_accesses:
                sa.is_deleted = self.is_deleted
                sa.save()
            contents = get_contents(self.space, not self.is_deleted)
            for content in contents:
                content.is_deleted = self.is_deleted
                content.save()
                libraries.utility.queues.trigger_backend_task('/search/put/%s' % content.id, target=get_versioned_module('localization'), queue_name='search', countdown=30)
                for cs in content.contentspace_set.all():
                    cs.is_deleted = self.is_deleted
                    update_content_space(cs)

        space_id_for_space_changed = self.space.id if self.space.is_second_level() else self.space.parent.id
        kids_for_space_changed.send(None, space_id=space_id_for_space_changed)


class ArchiveSpaceAsyncView(AbstractJobAsync):
    success_subject = 'Archiving publication succesed'
    success_message = 'Archiving publication {0} succesfully finished.'
    failure_message = 'There were errors archiving publication {0}.'
    failure_subject = 'Archiving publication failed.'
    admin_mail_title = 'Archive job project async failed'
    is_deleted = True


class RetrieveSpaceAsyncView(AbstractJobAsync):
    success_subject = 'Retrieving publication succesed'
    success_message = 'Retrieving publication {0} succesfully finished.'
    failure_message = 'There were errors Retrieving publication {0}.'
    failure_subject = 'Retrieving publication failed.'
    admin_mail_title = 'Retrieve job project async failed'
    is_deleted = False


class DeleteSpaceAsyncView(AbstractJobAsync):
    success_subject = 'Delete publication successfully deleted.'
    success_message = 'Delete publication {0} has finished with success.'
    failure_message = 'Deleting has failed.'
    failure_subject = 'Deleting project has failed.'
    admin_mail_title = 'Delete job project async failed'
    is_deleted = True

    def execute(self):
        publication = self.space
        while not publication.parent.is_second_level():
            publication = publication.parent

        if self.space != publication:
            for space in get_spaces_subtree(self.space.id):
                for content_space in space.contentspace_set.all():
                    content = content_space.content
                    is_deleted = content_space.is_deleted
                    remove_content_space(content_space)
                    add_content_to_space(content, publication, is_deleted=is_deleted)
                space.spaceaccess_set.all().delete()
                space.is_deleted = self.is_deleted
                space.save()

        space_id_for_space_changed = self.space.id if self.space.is_second_level() else self.space.parent.id
        kids_for_space_changed.send(None, space_id=space_id_for_space_changed)


@login_required
@has_space_access(Permission.SPACE_EDIT)
def projectControl(request, space_id):
    project = Space.objects.get(pk=space_id)
    spaces_list = project.kids.filter(is_deleted = False)
    spaces = sorted(spaces_list, key=lambda space: space.rank)
    token, token_key = create_publication_action_token(request.user)
    return render(request, 'corporate/subproject.html', {
        'spaces': spaces,
        'project': project,
        'token_key': token_key,
        'token': token
    })

@login_required
@has_space_access(Permission.SPACE_EDIT)
def ajax_subprojects(request, space_id):
    space = get_object_or_404(Space, pk=request.GET.get('id'))

    token_key = 'token_{0}'.format(TOKEN_KEYS.PUBLICATION_ACTION)
    token_value = request.GET.get(token_key)

    return render(request, 'corporate/children_corporate.html', {
        'spaces' : sorted(space.kids.all(), key=lambda space: space.rank),
        'project_id' : space_id,
        'token_key': token_key,
        'token': token_value
    })

@login_required
@has_space_access(Permission.SPACE_EDIT)
def addSubproject(request, space_id):
    project = get_object_or_404(Space, id=space_id)
    space = Space(title=project.title + "_sub", space_type=SpaceType.CORPORATE, parent=project)
    insert_space(space)
    messages.info(request, "Changes to the access rights in your company structure will be propagated in the background. This process can take up to a few minutes.")
    company_structure_changed.send(None, company_id=request.user.company.id, user_id=request.user.id)
    space_id_for_space_changed = space.pk if space.is_second_level() else space.parent.id
    kids_for_space_changed.send(None, space_id=space_id_for_space_changed)
    return HttpResponseRedirect('/corporate/' + request.GET.get('project') + '/subproject')

@login_required
@has_space_access(Permission.SPACE_EDIT)
def project_list(request, space_id):
    if space_id is None:
        raise Http404

    archived = False
    if 'archived' in request.GET:
        archived = True

    project = Space.objects.get(pk=space_id)
    company_structure_changed.send(None, company_id=request.user.company.id, user_id=request.user.id)

    sub_menus = [
        ('Archive', '/corporate/projects/{0}?archived=1'.format(project.id)),
        ('Backup project', '/backup/%s/select' % project.id),
        ('Update templates', '/bulk/templates/%s?next=/corporate/projects/%s' % (project.id, project.id)),
        ('Update assets', '/bulk/assets/%s' % project.id)
    ]

    spaces = project.kids.filter(is_deleted = archived).order_by('title')
    token, token_key = create_publication_action_token(request.user)
    context = {
        'spaces': spaces,
        'space_id': space_id,
        'project': project,
        'sub_menus': sub_menus,
        'token': token,
        'token_key': token_key
    }

    if not archived:
        return render(request, 'corporate/edit_projects.html',  context)
    else:
        return render(request, 'corporate/archived.html',  context)

@login_required
def change_template(request):
    if request.user.company is None:
        raise Http404
    if request.method == "POST":
        template_id = request.POST.get('template')
        if template_id == 'none':
            return _delete_default_template(request)
        content = Content.get_cached(id=template_id)
        st = SpaceTemplate.objects.filter(space=request.user.company)
        if len(st) == 0:
            space_template = SpaceTemplate(space=request.user.company, template=content)
            space_template.save()
        else:
            st[0].template = content
            st[0].save()
        messages.info(request, 'Default template changed.')
    st = SpaceTemplate.objects.filter(space=request.user.company)
    current_id = 0
    if len(st) > 0:
        current_id = st[0].template.id
    return render(request, 'corporate/change_template.html', {'current_id' : current_id})

def _delete_default_template(request):
    st = SpaceTemplate.objects.filter(space=request.user.company)
    if len(st) > 0:
        st[0].delete()
        messages.info(request, 'Default template changed to None.')
    return HttpResponseRedirect('/corporate/change_template')

def flush_user_cache(request, company_id):
    company_structure = get_spaces_tree(company_id)
    users = set()
    for space in company_structure:
        for sa in space.spaceaccess_set.all():
            users.add(sa.user)
    for user in users:
        user_spaces_flush(user)
    return HttpResponse("OK")

@login_required
@has_space_access(Permission.CONTENT_COPY)
def copy_to_account(request, content_id):
    if request.POST:
        form = CopyToAccount(request.POST)
        if form.is_valid():
            username = request.POST['user']
            user = User.objects.get(username=username)
            content = Content.get_cached(id=content_id)
            copy = content.makeCopy(True, user)
            space = get_private_space_for_user(user)
            add_content_to_space(copy, space)
            messages.info(request, 'Lesson copied to account <%s>' % user.username)
            return get_redirect(request)
    else:
        form = CopyToAccount()
    return render(request, 'corporate/copy_to_account.html', {'content_id' : content_id, 'next' : get_redirect_url(request), 'form' : form})

@login_required
@has_space_access(Permission.SPACE_EDIT)
def toggle_include_contents_in_editor(request, project_id):
    project = get_object_or_404(Space, pk=project_id)
    project.include_contents_in_editor = not project.include_contents_in_editor
    update_space(project, propagate_update=False) #update propagation would trigger recalculation of access rights for the whole company)
    cache.delete('templates_for_%s' % (request.user.company))
    addon_published.send(sender=None, company_id=request.user.company.id)
    return HttpResponseRedirect('/corporate/divisions')

def bug_track_add_form(request):
    return render(request, 'corporate/bug_track_add_form.html')

@login_required
def more_projects_dashboard(request):
    if request.user.company is None:
        locked_companies = get_locked_companies(request.user)
        for locked_company in locked_companies:
            messages.warning(request, 'The company account "%(company)s" has been locked. Please contact administrator' % { 'company' : locked_company })
        return HttpResponseRedirect('/mycontent')

    projects = get_projects_with_publications(request, lambda s: s.modified_date)

    projects_per_page, projects_per_page_string = get_values_per_page(request, 'projects', len(projects), 1000)
    paginator = Paginator(projects, projects_per_page)

    page_number = int(request.GET.get('page')) if 'page' in request.GET and re.search("^[\d]+$", request.GET.get('page')) else 0

    if page_number > 0:
        if page_number < paginator.num_pages:
            page_content = paginator.page(page_number)
        else:
            page_content = paginator.page(paginator.num_pages)
    else:
        page_content = paginator.page(1)

    page_contents = list(page_content.object_list)

    recently_opened = get_recently_opened(request.user)

    token, token_key = create_mycontent_editor_token(request.user)
    return render(request, 'corporate/more_projects.html', { 
                    'projects': page_contents, 
                    'paginator' : paginator, 
                    'current_page' : page_content,
                    'projects_per_page_dict' : { 'values_per_page' : projects_per_page_string },
                    'recently_opened' : recently_opened,
                    'token': token,
                    'token_key': token_key,
                    'is_company_locked' : is_company_locked(request.user.company),
                    })


@login_required
@user_passes_test(lambda user: user.is_superuser)
def clear_news_cache(request):
    cache.delete('home_index:latest_news')

    messages.success(request, 'News cache cleared')

    return HttpResponseRedirect('/user/settings')


def copy_to_demo_account(request, content_id, space_id = None):
    if space_id is None:
        space = get_private_space_for_user(request.user)
    else:
        space = get_object_or_404(Space, id=space_id)

    try:
        content = Content.get_cached(id=content_id)
    except Content.DoesNotExist:
        return

    copy = content.makeCopy(False, request.user)

    if copy.content_type != ContentType.ADDON:
        copy.add_title_to_xml()

    copy_metadata(content, copy)
    add_content_to_space(copy, space)

    metadata_updated.send(sender=None, content_id=copy.id)


def add_division_to_demo_account(request, space_id, title):
    if request.method == 'POST':
        parent = Space.objects.get(pk=space_id)
        space = Space(title=title, parent=parent, space_type=parent.space_type)
        insert_space(space)
        kids_for_space_changed.send(None, space_id=space_id)
        company_structure_changed.send(None, company_id=space.top_level.id, user_id=request.user.id)


def set_include_contents_in_editor_demo_account(space, project_id):
    project = get_object_or_404(Space, pk=project_id)
    project.include_contents_in_editor = True
    update_space(project, propagate_update=False) #update propagation would trigger recalculation of access rights for the whole company)
    cache.delete('templates_for_%s' % space)
    addon_published.send(sender=None, company_id=space.id)


def add_demo_content(request, space):
    demo_lessons = get_object_or_none(DemoAccountLessons)
    if demo_lessons is None:
        demo_lessons = DemoAccountLessons()
        demo_lessons.save()

    #add projects
    add_division_to_demo_account(request, space.id, 'Sample Lessons')
    add_division_to_demo_account(request, space.id, 'Sample Templates')

    #add lesson to My Content
    copy_to_demo_account(request, demo_lessons.my_content_demo_lesson)

    #add publication to Sample Lessons
    project_space = Space.objects.get(parent=space, title='Sample Lessons')
    add_division_to_demo_account(request, project_space.id, 'Demo')

    #add lessons to publication
    publication_space = Space.objects.get(parent=project_space)
    copy_to_demo_account(request, demo_lessons.publication_lesson_first, publication_space.id)
    copy_to_demo_account(request, demo_lessons.publication_lesson_second, publication_space.id)
    copy_to_demo_account(request, demo_lessons.publication_lesson_third, publication_space.id)

    #add publication to Sample Templates
    template_space = Space.objects.get(parent=space, title='Sample Templates')
    add_division_to_demo_account(request, template_space.id, 'Templates')

    # add lessons to template publication
    publication_template_space = Space.objects.get(parent=template_space)
    copy_to_demo_account(request, demo_lessons.template_lesson_first, publication_template_space.id)
    copy_to_demo_account(request, demo_lessons.template_lesson_second, publication_template_space.id)
    copy_to_demo_account(request, demo_lessons.template_lesson_third, publication_template_space.id)
    set_include_contents_in_editor_demo_account(space, template_space.id)


def create_trial_account(request):
    if request.user.is_authenticated():
        if request.user.company is not None:
            return HttpResponseRedirect('/mycontent')
        if request.method == 'POST':
            name = request.POST.get("space_name")
            if len(name) > 0:
                if not request.user.company:
                    user = User.objects.get(username = request.user)

                    space = Space(title = name, space_type = 3, is_test=True)
                    insert_space(space)
                    space_public = Space(title = space.title + ' Public', space_type = 2)
                    insert_space(space_public)

                    role = Role(name = 'owner', permissions = Permission().get_all(), company = space)
                    role.save()
                    space_access = SpaceAccess(user=user, space=space, roles = [role.pk])
                    space_access.save()
                    create_company_user(space, user)
                    cps = CorporatePublicSpace(company = space, public_category = space_public)
                    cps.save()
                    properties = CompanyProperties(company = space)

                    now = datetime.datetime.now()
                    valid_date = now + datetime.timedelta(days=30)
                    properties.valid_until = valid_date
                    properties.max_accounts = 3
                    properties.save()
                    messages.info(request, 'Company <%s> created and user <%s> is an owner' % (space.title, user.username))
                    delete_template_fragment_cache('menu', user)

                    add_demo_content(request, space)

                    mail_admins('New 30 days trial account', 'New 30 days trial account has been created by user: %s' % (request.user))

                    message = render_to_string('emails/trial_activation_completed.txt', {})

                    send_mail('30 days FREE TRIAL activation process completed',
                              message, settings.SERVER_EMAIL, [request.user.email])

                    return HttpResponseRedirect('/mycontent')
                else:
                    messages.info(request, 'You already have company space')
                    return HttpResponseRedirect('/mycontent')

        return render(request, 'public/create_trial_account.html')
    else:
        return render(request, 'public/login_register_info.html')


def no_space_info(request):
    if request.user.company is not None and is_company_locked(request.user.company):
        return HttpResponseRedirect('/mycontent')

    return render(request, 'corporate/no_space_info.html')


def set_demo_sample_lessons(request):
    demo_lessons = get_object_or_none(DemoAccountLessons)
    if demo_lessons is None:
        demo_lessons = DemoAccountLessons()
        demo_lessons.save()

    if request.method == 'POST':
        demo_lessons.set_my_content_demo_lesson(request.POST.get("my_content_lesson"))
        demo_lessons.set_publication_lesson_first(request.POST.get("publication_lesson_first"))
        demo_lessons.set_publication_lesson_second(request.POST.get("publication_lesson_second"))
        demo_lessons.set_publication_lesson_third(request.POST.get("publication_lesson_third"))
        demo_lessons.set_template_lesson_first(request.POST.get("template_lesson_first"))
        demo_lessons.set_template_lesson_second(request.POST.get("template_lesson_second"))
        demo_lessons.set_template_lesson_third(request.POST.get("template_lesson_third"))
        demo_lessons.save()

        messages.info(request, 'Lessons have been set')

    return render(request, 'corporate/set_demo_sample_lessons.html', {
                    'lessons': demo_lessons
                    })