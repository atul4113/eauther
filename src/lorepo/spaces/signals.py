import django.dispatch
from libraries.utility.cacheproxy import own_cache_mutex_try
from libraries.utility.environment import get_versioned_module
from libraries.utility.queues import trigger_backend_task

space_access_changed = django.dispatch.Signal(providing_args=['user_id', 'new_space_id'])
company_structure_has_changed = django.dispatch.Signal(providing_args=['company_id'])

def update_user_space_permissions(sender, user_id, new_space_id = None, action=None, **kwargs):
    if new_space_id:
        name = "musp%ss%s"%(user_id, new_space_id)
        if own_cache_mutex_try(name):
            trigger_backend_task('/spaces/_make_user_space_permission/%s/%s' % (user_id,new_space_id),
                                         target=get_versioned_module('localization'),
                                         queue_name='localization',
                                         params = {'action':action})

    else:
        name = "musp%s"%(user_id)
        if own_cache_mutex_try(name):
            trigger_backend_task('/spaces/_make_user_space_permission/%s' % (user_id),
                                         target=get_versioned_module('localization'),
                                         queue_name='localization')



def update_company_users_space_permissions(sender, **kwargs):
    company_id = kwargs['company_id']
    name = "mcusp%s"%(company_id)
    if own_cache_mutex_try(name):
        trigger_backend_task('/spaces/make_company_user_space_permissions_backend/%s' % (company_id),
                                     target=get_versioned_module('localization'),
                                     queue_name='localization')

