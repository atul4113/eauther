from django.http import Http404
from src.libraries.utility.helpers import get_object_or_none
from src.lorepo.permission.models import PermissionTuples, Role, Permission
import logging
from src.lorepo.corporate.models import CompanyUser
from src.lorepo.spaces.models import UserSpacePermissions, SpaceType, SpaceAccess
from src.lorepo.spaces.util import get_space_for_content, has_space_permission
from django.core.exceptions import PermissionDenied
import src.libraries.utility.cacheproxy as cache


def translate_perm_to_tuple(integer_perm):
    if integer_perm in PermissionTuples:
        return PermissionTuples[integer_perm]
    else:
        logging.info('Missing Permission Label [%s]' % str(integer_perm))
        return str(integer_perm)


def group_permissions_tuples(permissions_tuples):
    group = {}

    for perm_tuple in permissions_tuples:
        if not perm_tuple[0] in group:
            group[perm_tuple[0]] = [perm_tuple[1]]
        else:
            group[perm_tuple[0]].append(perm_tuple[1])

    return group


def translate_perm_to_integer(perm):
    for key, value in list(PermissionTuples.items()):
        if value[1] == perm:
            return key


def create_company_user(company, user):
    return CompanyUser.objects.get_or_create(user=user, username=user.username, company=company)


def remove_company_user(company, user, company_user=None):
    if company_user is None:
        company_user = get_object_or_none(CompanyUser, company=company, user=user)

    if company_user is None:
        raise Http404("Company user for user id: {0} does not exists".format(user.id))

    space_accesses = SpaceAccess.objects.filter(user=company_user.user)
    corporate_space_accesses = [space_access for space_access in space_accesses if space_access.space.space_type == SpaceType.CORPORATE]
    for sa in corporate_space_accesses:
        sa.delete()

    company_user.delete()


def get_company_for_user(user):
    query_result = CompanyUser.objects.filter(user = user)
    return query_result[0].company if query_result.count() > 0 else None


def get_company_users(company):
    company_users = cache.get('company_%s_users' % company.id)

    if company_users is None:
        company_users = CompanyUser.objects.filter(company = company).order_by('username')
        cache.set('company_%s_users' % company.id, company_users, timeout= 24*60*60)

    return company_users


def get_projects_users(company, projects):
    all_projects_users = []

    company_users = CompanyUser.objects.filter(company=company)
    company_users_map = {}
    for company_user in company_users:
        company_users_map[company_user.user.id] = company_user

    for project in projects:
        project_users = cache.get('project_%s_users' % project.id)
        if project_users is None:
            space_accessess = list(SpaceAccess.objects.filter(space=project))
            for publication in project.publications:
                space_accessess.extend(list(SpaceAccess.objects.filter(space=publication)))

            project_users = [space_access.user for space_access in space_accessess]
            project_users = [company_users_map[project_user.id] for project_user in project_users]
            project_users.sort(key=lambda x: x.username)
            cache.set('project_%s_users' % project.id, project_users)
        all_projects_users.extend(project_users)

    all_projects_users = list(set(all_projects_users))
    all_projects_users.sort(key=lambda cu: cu.username)
    return all_projects_users


def check_space_access(space, user, permission):
    if verify_space_access(space, user, permission):
        return True
    raise PermissionDenied


def verify_space_access(space, user, permission):
    if user.is_superuser:
        return True
    usp = UserSpacePermissions.get_cached_usp_for_user(user)
    permissions = usp.get_permissions_for_space(space.id)
    if permissions and permission in permissions:
        return True
    return False


def verify_content_access(content, user, permission):
    space = get_space_for_content(content)
    return verify_space_access(space, user, permission)


def get_user_permissions(space_access):
    permissions = set()
    if space_access:
        if space_access.user.is_superuser:
            return set(Permission().get_all())

        user_roles = Role.objects.filter(pk__in = space_access.roles)
        for role in user_roles:
            permissions.update(role.permissions)

    return permissions


def get_values_per_page(request, key, max_value, default_value = 10):
    values_per_page_session = request.session.get('values_per_page_%s' % key, None)
    values_per_page_get = request.GET.get('values_per_page', None)

    if values_per_page_session and not values_per_page_get:
        if values_per_page_session == 'all':
            values_per_page = max_value
            values_per_page_string = 'all'
        else:
            values_per_page = int(values_per_page_session)
            values_per_page_string = str(values_per_page_session)

    elif values_per_page_session and values_per_page_get:
        if values_per_page_get == 'all':
            values_per_page = max_value
            values_per_page_string = 'all'
        else:
            values_per_page = int(values_per_page_get)
            values_per_page_string = str(values_per_page)

    else:
        values_per_page = default_value
        values_per_page_string = str(default_value)

    request.session['values_per_page_%s' % key] = values_per_page

    return values_per_page, values_per_page_string


def get_projects_and_publications(user, company):
    publications = cache.get_for_user(user, 'manage_access_publications')
    projects = cache.get_for_user(user, 'manage_access_projects')

    if publications is None or projects is None:
        publications = []
        projects = []
        if has_space_permission(company, user, 'SPACE_ACCESS_MANAGE'):
            projects = list(company.kids.filter(is_deleted=False))
            for project in projects:
                loaded_kids = list(project.kids.filter(is_deleted=False))
                project.publications = loaded_kids
                publications.extend(loaded_kids)
        else:
            for division in list(user.divisions.values()):
                if has_space_permission(division, user, 'SPACE_ACCESS_MANAGE'):
                    loaded_kids = list(division.kids.filter(is_deleted=False))
                    division.publications = loaded_kids
                    projects.append(division)
                    publications.extend(loaded_kids)
        cache.set_for_user(user, 'manage_access_publications', publications)
        cache.set_for_user(user, 'manage_access_projects', projects)

    return projects, publications
