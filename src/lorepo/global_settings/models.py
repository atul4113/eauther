from djangae.fields import JSONField

import libraries.utility.cacheproxy as cache
from lorepo.util.singleton_model import SingletonModel


class GlobalSettings(SingletonModel):
    referrers = JSONField()

    CACHE_KEY = 'global_settings'
    CACHE_TIME = 24 * 60 * 60 * 7

    def save(self, *args, **kwargs):
        super(GlobalSettings, self).save(*args, **kwargs)
        self.set_cache()

    def set_cache(self):
        cache.set(self.CACHE_KEY, self, timeout=self.CACHE_TIME)

    @classmethod
    def get_cached(cls):
        global_settings = cache.get(cls.CACHE_KEY)
        if not global_settings:
            global_settings = cls.load()
            global_settings.set_cache()
        return global_settings
