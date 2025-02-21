# -*- coding: utf-8 -*-
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from libraries.utility.decorators import backend
from libraries.utility.environment import get_versioned_module
from libraries.utility.queues import trigger_backend_task
from lorepo.permission.util import get_company_for_user
from lorepo.spaces.models import Space, SpaceType, UserSpacePermissions
from django.contrib.auth.decorators import login_required, user_passes_test
from lorepo.spaces.form import SpaceForm, RankForm
from django.http import HttpResponseRedirect, HttpResponse
from lorepo.spaces.signals import space_access_changed
from lorepo.spaces.util import get_user_spaces, get_top_level_public_spaces, \
    get_spaces_subtree, SpacePermissionGenerator
from lorepo.spaces.model.companyspacemap.company_space_map import CompanySpaceMap
from django.contrib.auth.models import User
import libraries.utility.cacheproxy as cache
from lorepo.spaces.service import update_space, insert_space
from libraries.utility.redirect import get_redirect, get_redirect_url
from lorepo.mycontent.service import add_content_to_space, remove_content_space
from lorepo.corporate.signals import kids_for_space_changed
from lorepo.permission.decorators import has_space_access
from lorepo.permission.models import Permission
from mauthor.company.util import get_users_from_company
from lorepo.spaces.model.companyspacemap.multitasks_locker import CompanySpaceMapTaskLocker

@login_required
def index(request, space_id = None):

    if space_id is None:
        spaces = get_user_spaces(request.user)
    else:
        spaces = get_spaces_subtree(space_id)
        space = Space.objects.get(pk=space_id)
        spaces.remove(space)

    for space in spaces:
        content_spaces = space.contentspace_set.all()
        space.size = len([cs for cs in content_spaces if not cs.is_deleted])

    return render(request, 'spaces/index.html', {'spaces' : sorted(spaces, key=lambda space: space.title), 'space_id' : space_id })


@login_required
@user_passes_test(lambda u: u.is_superuser)
@backend
def undelete_project(request):
    """ Undelete project and assign it to a specified company"""
    project_id = request.GET.get('project_id', '0')
    company_id = request.GET.get('company_id', '0')

    project = get_object_or_404(Space, pk=project_id)
    company = get_object_or_404(Space, pk=company_id)

    project.is_deleted = False
    project.parent = company
    project.top_level = company
    project.path = company.path + [int(project_id)]
    project.save()

    return make_company_user_space_permissions(request, company_id)


@login_required
def publicSpaceControl(request):
    spaces = get_top_level_public_spaces()
    spaces = sorted(spaces, key=lambda space: space.rank)
    return render(request, 'spaces/public.html', { 'spaces' : spaces })


@login_required
def addPublicSpace(request):
    newSpace(request, True, None)
    return HttpResponseRedirect('/spaces/public_space')


@login_required
@has_space_access(Permission.SPACE_EDIT)
def addSpace(request, space_id = None, **kwargs):
    newSpace(request, False, space_id)
    kids_for_space_changed.send(None, space_id=space_id)
    try:
        space = request.kwargs['space']
        if space.is_private():
            space_access_changed.send(None, user_id = request.user.id)
    except:
        pass
    return get_redirect(request)

@login_required
@has_space_access(Permission.SPACE_EDIT)
def addSubspace(request, space_id):
    parent = get_object_or_404(Space, id=space_id)
    space = Space(title=parent.title + "_sub", space_type=SpaceType.PUBLIC, parent=parent)
    insert_space(space)
    messages.info(request, "Changes to the access rights in your company structure will be propagated in the background. This process can take up to a few minutes.")
    cache.delete_for_user(request.user, 'copy_spaces')
    return get_redirect(request, '/corporate/publicspaces')

def newSpace(request, is_public, space_id):
    if request.method == 'POST':
        form = SpaceForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            if is_public is True:
                space = Space(title=title, space_type=SpaceType.PUBLIC)
            else:
                if space_id is not None:
                    parent = Space.objects.get(pk=space_id)
                    space = Space(title=title, parent=parent, space_type=parent.space_type)
                else:
                    spaces = list(get_user_spaces(request.user))
                    parent = [space for space in spaces if space.parent == None][0]
                    space = Space(title=title, parent=parent)
            insert_space(space)
            messages.info(request, "Changes to the access rights in your company structure will be propagated in the background. This process can take up to a few minutes.")
            cache.delete_for_user(request.user, 'copy_spaces')
            
def _rename(request, space_id, is_public, template):
    space = get_object_or_404(Space, id=space_id)
    next_url = request.GET.get('next', '/')
    if request.method == 'POST':
        form = SpaceForm(request.POST)
        if form.is_valid():
            space.title = form.cleaned_data['title']
            if 'next' in form.data:
                next_url = form.data['next']
            update_space(space, propagate_update=False) #update propagation would trigger recalculation of access rights for the whole company
            cache.delete_for_user(request.user, 'copy_spaces')
            if is_public is False:
                if next_url == '':
                    url = '/spaces/%(space_id)s' % {'space_id' : space.parent.id }
                else:
                    url = next_url
                return HttpResponseRedirect(url)
            else:
                return get_redirect(request, '/corporate/publicspaces')
    return render(request, template, {'space' : space, 'next' : next_url})

@login_required
@has_space_access(Permission.SPACE_EDIT)
def renameSpace(request, space_id):
    return _rename(request, space_id, False, 'spaces/rename.html')

@login_required
@has_space_access(Permission.SPACE_EDIT)
def renameProject(request, space_id, template):
    space = get_object_or_404(Space, pk=space_id)
    space_id_for_space_changed = space.id if space.is_second_level() else space.parent.id
    kids_for_space_changed.send(None, space_id=space_id_for_space_changed)
    return _rename(request, space_id, False, template)

@login_required
@has_space_access(Permission.SPACE_EDIT)
def renamePublicSpace(request, space_id):
    return _rename(request, space_id, True, 'spaces/rename.html')

@login_required
@has_space_access(Permission.SPACE_EDIT)
def rank(request, space_id, template='spaces/rank.html'):
    next_url = get_redirect_url(request)
    form = None
    space = get_object_or_404(Space, id=space_id)
    if request.method == 'POST':
        form = RankForm(request.POST)
        if form.is_valid():
            space.rank = form.cleaned_data['rank']
            update_space(space, propagate_update=False) #update propagation would trigger recalculation of access rights for the whole company
            space_id_for_space_changed = space.id if space.is_second_level() else space.parent.id
            kids_for_space_changed.send(None, space_id=space_id_for_space_changed)
            return get_redirect(request, '/corporate/publicspaces')
    return render(request, template, {'space' : space, 'form' : form, 'next' : next_url})


@login_required
def _delete(request, space_id, is_public):
    space = get_object_or_404(Space, id=space_id)
    parent = space.parent
    for content_space in space.contentspace_set.all():
        if parent is not None:
            add_content_to_space(content=content_space.content, space=parent, is_deleted=content_space.is_deleted)
        remove_content_space(content_space)
    space.spaceaccess_set.all().delete()
    space.delete()
    cache.delete_for_user(request.user, 'copy_spaces')
    if is_public is False:
        url = '/spaces/%(space_id)s' % {'space_id' : parent.id}
        return HttpResponseRedirect(url)
    else:
        return get_redirect(request, target="corporate/publicspaces")
    
@login_required
@has_space_access(Permission.SPACE_REMOVE)
def deleteSpace(request, space_id):
    return _delete(request, space_id, False)

@login_required
@has_space_access(Permission.SPACE_REMOVE)
def deletePublicSpace(request, space_id):
    return _delete(request, space_id, True)

@login_required
@user_passes_test(lambda user: user.is_superuser)
def fixdb_make_all_user_space_permissions(request):
    count = User.objects.filter(is_active=True).count()
    offset = 0
    step = 200
    queryset = User.objects.filter(is_active=True)
    while offset < count:
        user_ids = queryset.values_list('id',flat=True)[offset:offset+step]
        offset = offset + step
        for user_id in user_ids:
            name = "musp%s"%(user_id)
            if cache.own_cache_mutex_try(name):
                trigger_backend_task('/spaces/_make_user_space_permission/%s' % (user_id),
                                         target=get_versioned_module('localization'),
                                         queue_name='localization')
    return HttpResponse('Job started')

@login_required
@user_passes_test(lambda user: user.is_superuser)
def make_all_companies_space_permissions(request):
    companies = Space.objects.filter(space_type=SpaceType.CORPORATE, parent=None, is_deleted=False)
    for company in companies:
        name = "mcusp%s"%(company.id)
        if cache.own_cache_mutex_try(name):
            trigger_backend_task('/spaces/make_company_user_space_permissions_backend/%s' % (company.id),
                                     target=get_versioned_module('localization'),
                                     queue_name='localization')
    return HttpResponseRedirect('/')


@login_required
@user_passes_test(lambda user: user.is_superuser)
def make_company_user_space_permissions(request, company_id):
    company = get_object_or_404(Space, pk = company_id)
    _make_company_user_space_permissions(company)
    messages.info(request, 'User access rights will be recalculated - this might take several minutes.')
    return HttpResponseRedirect("/company/details/%s"%(company_id))

@backend
def make_company_user_space_permissions_backend(request, company_id):
    CompanySpaceMapTaskLocker(company_id).open()
    company = get_object_or_404(Space, pk = company_id)
    _make_company_user_space_permissions(company)
    return HttpResponse()


def _make_company_user_space_permissions(company):
    name = "mcusp%s"%(company.id)
    cache.free_cache_mutex(name)
    CompanySpaceMap.fresh(company.id)
    users = get_users_from_company(company)
    for user in users:
        name = "musp%s"%(user.id)
        cache.delete_for_user(user, 'divisions')
        if cache.own_cache_mutex_try(name):
            trigger_backend_task('/spaces/_make_user_space_permission/%s' % (user.id),
                                     target=get_versioned_module('localization'),
                                     queue_name='localization')

@backend
def make_user_space_permission_backend(request, user_id, new_space_id=None):
    if new_space_id:
        name = "musp%ss%s"%(user_id,new_space_id)
    else:
        name = "musp%s"%(user_id)
    cache.free_cache_mutex(name)
    user = get_object_or_404(User, pk = user_id)
    try:
        usp, usp_created = UserSpacePermissions.objects.get_or_create(user=user)
    except UserSpacePermissions.MultipleObjectsReturned:
        UserSpacePermissions.objects.filter(user=user).delete()
        usp, usp_created = UserSpacePermissions.objects.get_or_create(user=user)

    s_perm_gen = SpacePermissionGenerator(user_id, new_space_id, request.POST.get('action', None))  #ha ha
    try:
        company_id = get_company_for_user(user).id
        company_space_map  = CompanySpaceMap.cached(company_id)
    except:
        company_space_map  = CompanySpaceMap()
    s_perm_gen.set_map(company_space_map)

    if not usp_created:
        usp.clear_permissions()
    if user.is_superuser:
        all_perm = Permission().get_all()
        for space_id in s_perm_gen.user_spaces_ids():
            usp.add_space_permissions(space_id, all_perm)
    else:
        s_perm_gen.calculate_space_permissions(usp)
    usp.save()
    cache.delete("is_any_division_admin_%s"%(user_id))
    return HttpResponse()
