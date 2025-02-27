from django.core.cache import cache
from src.libraries.utility.queues import trigger_backend_task
from src.libraries.utility.environment import get_versioned_module


class MultiTasksLocker:
    CSM_MUTEX_NOT_WORK = 0
    CSM_MUTEX_WORK = 1
    cache_timeout = 300  # Cache timeout in seconds
    default_version = 'download'
    queue_name = 'localization'
    target = get_versioned_module('download')
    backend_task_url = "backend task url"
    cache_prefix = "Cache name for flag"

    def __init__(self, company_id):
        self.trigger_url = self.backend_task_url.format(company_id)
        self.cache_name = self.cache_prefix.format(company_id)

    def trigger(self):
        """
        Call a new task and set a flag.
        If multiple users try to execute the task with the same cache ID,
        only one task will be called.
        After the task completes, it must clear the flag.
        """
        # Set the initial flag if it doesn't exist
        cache.add(self.cache_name, self.CSM_MUTEX_NOT_WORK, self.cache_timeout)

        # Use Django's cache to check and set the flag atomically
        with cache.lock(self.cache_name + "_lock"):
            csm_flag = cache.get(self.cache_name)
            if csm_flag == self.CSM_MUTEX_NOT_WORK:
                cache.set(self.cache_name, self.CSM_MUTEX_WORK, self.cache_timeout)
                trigger_backend_task(self.trigger_url, self.target, queue_name=self.queue_name)

    def close(self):
        """Set the flag to indicate the task is not running."""
        return self._set_flag(self.CSM_MUTEX_NOT_WORK)

    def open(self):
        """Set the flag to indicate the task is running."""
        return self._set_flag(self.CSM_MUTEX_WORK)

    def isCalculating(self):
        """Check if the task is currently running."""
        return cache.get(self.cache_name)

    def _set_flag(self, value):
        """Set the flag to the specified value."""
        if cache.add(self.cache_name, value, self.cache_timeout):
            return True
        with cache.lock(self.cache_name + "_lock"):
            cache.set(self.cache_name, value, self.cache_timeout)
            return True


class CompanySpaceMapTaskLocker(MultiTasksLocker):
    cache_prefix = 'company_space_map_flag_{0}'
    backend_task_url = '/spaces/make_company_user_space_permissions_backend/{0}'