from src.libraries.utility.environment import RequestCache
from django.core.cache import cache


class CacheCleanerMixin(object):
    """
        Clear cache in project for each test.
    """
    def setUp(self):
        super(CacheCleanerMixin, self).setUp()
        cache.clear()
        RequestCache.flush()
