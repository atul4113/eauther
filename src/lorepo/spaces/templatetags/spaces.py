from django.template.defaultfilters import register
from src.lorepo.corporate.models import CompanyUser
from src.lorepo.spaces.models import Space
from src.lorepo.spaces.util import is_company_locked
from src.lorepo.spaces.util import is_space_owner as is_space_owner_util
from src.lorepo.corporate.utils import get_division_for_space
from src.mauthor.company.util import get_company_properties


@register.filter
def has_kids(space):
    if space.kids.all():
        return True

@register.inclusion_tag('public/children.html')
def children_tag_spaces_list(spaces, selected_space):
    spaces = sorted(spaces, key=lambda space: space.rank)
    return {'spaces': spaces, 'selected_space' : selected_space }

@register.inclusion_tag('spaces/children.html')
def children_tag(spaces):
    spaces = sorted(spaces, key=lambda space: space.rank)
    return {'spaces': spaces }

@register.inclusion_tag('mycontent/children.html')
def children_tag_select(spaces, param, selected_space):
    return {'param' : param, 'selected_space' : selected_space, 'spaces' : spaces}

@register.filter
def is_subspace(subspace, space):
    while subspace.parent is not None:
        if space == subspace.parent:
            return True
        subspace = subspace.parent
    return False

@register.filter
def is_space_owner_tag(space_id, user):
    if space_id is None:
        return False
    if user.is_superuser:
        return True
    space = Space.objects.get(pk=space_id)
    return is_space_owner_util(space, user)

@register.filter
def has_permission(space_access, permission):
    if space_access is None:
        return False
    return space_access.has_permission(permission)

@register.filter
def should_include_contents_in_editor(space):
    return get_division_for_space(space).include_contents_in_editor


@register.filter
def is_company_locked_for_user(company):
    return is_company_locked(company)

@register.filter
def is_doc_type(request):
    if 'type' in request.GET:
        return request.GET['type'] == 'doc'
    return '/doc' in request.path

@register.filter
def is_test_company(company_id):
    space = Space.objects.get(id=company_id)
    return space.is_test


@register.filter
def is_more_users_in_company(company):
    users = CompanyUser.objects.filter(company=company).count()
    company_properties = get_company_properties(company)
    if company_properties.max_accounts is not None and users > company_properties.max_accounts:
        return True
    return False
