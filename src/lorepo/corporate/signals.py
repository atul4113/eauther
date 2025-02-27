import django.dispatch
import src.libraries.utility.cacheproxy as cache
from django.contrib.auth.models import User
from hashlib import sha1 as sha_constructor
from django.shortcuts import get_object_or_404
from src.libraries.utility.queues import trigger_task
from src.lorepo.spaces.models import Space


company_structure_changed = django.dispatch.Signal()
access_rights_changed = django.dispatch.Signal()
kids_for_space_changed = django.dispatch.Signal()


def user_spaces_flush(user):
    cache.delete_for_user(user, 'copy_spaces')
    cache.delete_for_user(user, 'divisions')
    cache.delete_for_user(user, 'company')
    cache.delete_for_user(user, 'public_category')
    cache.delete_for_user(user, 'public_categories')
    cache.delete_for_user(user, 'manage_access_publications')
    cache.delete_for_user(user, 'manage_access_projects')


def flush_company_structure_cache(sender, **kwargs):
    company_id = kwargs['company_id']
    user_id = kwargs['user_id']
    if user_id:
        user = get_object_or_404(User, pk=user_id)
        user_spaces_flush(user)
    company = get_object_or_404(Space, pk = company_id)
    cache.delete('company_%s_users' % company_id)
    for project in company.kids.filter(is_deleted = False):
        cache.delete('project_%s_users' % project.id)

    trigger_task('/corporate/drop_cache/%s' % company_id)


def flush_spaces_for_user(sender, **kwargs):
    user_id = kwargs['user_id']
    user = User.objects.get(pk=user_id)
    user_spaces_flush(user)
    args = sha_constructor(user.username)
    cache_key = 'template.cache.%s.%s' % ('menu', args.hexdigest())
    cache.delete(cache_key)


def flush_kids_for_space(sender, **kwargs):
    space_id = kwargs['space_id']
    cache.delete('kid_spaces_for_%s' % space_id)

