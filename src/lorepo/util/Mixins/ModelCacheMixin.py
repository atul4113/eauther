from django.http import Http404

import src.libraries.utility.cacheproxy as cache


class ModelCacheMixin(object):
    CACHE_PREFIX = None

    @classmethod
    def set_cache(cls, id, value, timeout=30*60):
        cache.set(cls.CACHE_PREFIX % (str(id)), value, timeout=timeout)

    @classmethod
    def get_cached(cls, id, timeout=30*60):
        content = cache.get(cls.CACHE_PREFIX % (str(id)))
        if content:
            return content
        else:
            content = cls.objects.get(id=id)
            cls.set_cache(id, content, timeout=timeout)
            return content

    @classmethod
    def get_cache(cls, id):
        return cache.get(cls.CACHE_PREFIX % (str(id)))

    @classmethod
    def get_cached_or_none(cls, id):
        try:
            return cls.get_cached(id)
        except cls.DoesNotExist:
            return None

    @classmethod
    def get_cached_or_404(cls, id):
        try:
            return cls.get_cached(id)
        except cls.DoesNotExist:
            raise Http404()

    @classmethod
    def cache_delete(cls, id):
        cache.delete(cls.CACHE_PREFIX % str(id))