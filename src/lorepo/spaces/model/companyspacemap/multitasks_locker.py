import google.appengine.api.memcache as memcache
from libraries.utility.queues import trigger_backend_task
from libraries.utility.environment import get_versioned_module


# noinspection PyClassHasNoInit
class MultiTasksLocker(object):
    CSM_MUTEX_NOT_WORK = 0
    CSM_MUTEX_WORK = 1
    cache_timeout = 300
    default_version = 'download'
    queue_name = 'localization'
    target = get_versioned_module('download')
    backend_task_url = "backend task url"
    cache_prefix = "Cache name for flag"

    def __init__(self, company_id):
        self.trigger_url = self.backend_task_url.format(company_id)
        self.cache_name = self.cache_prefix.format(company_id)

    '''
    call new task and set flag.
    If more than one user will try execute task in the same time with the same cache id,
     then only one task will be called
    After work, task must clear flag.
    '''
    def trigger(self):
        memcache.add(self.cache_name, MultiTasksLocker.CSM_MUTEX_NOT_WORK, self.cache_timeout)
        client = memcache.Client()
        csm_flag = client.gets(self.cache_name)
        if csm_flag == MultiTasksLocker.CSM_MUTEX_NOT_WORK and client.cas(self.cache_name, MultiTasksLocker.CSM_MUTEX_WORK, self.cache_timeout):
            trigger_backend_task(self.trigger_url, self.target, queue_name=self.queue_name)

    def close(self):
        return self._set_flag(MultiTasksLocker.CSM_MUTEX_NOT_WORK)

    def open(self):
        return self._set_flag(MultiTasksLocker.CSM_MUTEX_WORK)

    def isCalculatin(self):
        client = memcache.Client()
        return client.gets(self.cache_name)

    def _set_flag(self, value):
        if memcache.add(self.cache_name, value, self.cache_timeout):
            return True
        client = memcache.Client()
        client.gets(self.cache_name)
        return client.cas(self.cache_name, value, self.cache_timeout)


class CompanySpaceMapTaskLocker(MultiTasksLocker):
    cache_prefix = 'company_space_map_flag_{0}'
    backend_task_url = '/spaces/make_company_user_space_permissions_backend/{0}'