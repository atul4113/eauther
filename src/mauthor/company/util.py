import src.libraries.utility.cacheproxy as cache

from src.lorepo.corporate.models import CompanyProperties
from src.lorepo.corporate.signals import company_structure_changed
from src.lorepo.permission.util import get_company_users
import src.settings as settings


def get_company_properties(company):
    properties_list = CompanyProperties.objects.filter(company=company)
    properties = properties_list[0] if properties_list else None
    if not properties:
        properties = CompanyProperties(company=company)
        properties.save()
    if not hasattr(properties, 'language_code'):
        properties.language_code = settings.LANGUAGE_CODE
    return properties


def get_users_from_company(company):
    company_users = get_company_users(company)
    users = set()
    for company_user in company_users:
        users.add(company_user.user)
    return users


def invalidate_language_cache_for_company_users(company):
    users = get_users_from_company(company)
    for user in users:
        cache.delete_for_user(user, 'language_code_bidi')


def remove_spaceaccesses(space):
    space_accesses = list(space.spaceaccess_set.all())

    for subspace in space.kids.all():
        # If in the future will be the ability to remove the publication
        # AND granting access on the module level
        # - here we'll have to extend the search of space_accesses for the next level
        space_accesses.extend(list(subspace.spaceaccess_set.all()))

    for space_access in space_accesses:
        company = space_access.space.top_level

        company_structure_changed.send(None, company_id=company.id, user_id=space_access.user_id)
        cache.delete_template_fragment_cache('menu', space_access.user)
        space_access.delete()
