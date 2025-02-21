from django.apps import AppConfig
from lorepo.mycontent.signals import content_updated, flush_content_cache


class MyContentConfig(AppConfig):
    name = 'lorepo.mycontent'
    verbose_name = 'Mycontent config'

    def ready(self):
        content_updated.connect(flush_content_cache, dispatch_uid="content_updated_connect_flush_content_cache")