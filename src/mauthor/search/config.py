from django.apps import AppConfig
from src.lorepo.mycontent.signals import metadata_updated, metadata_updated_async
from .signals import update_index_async, update_index_async_from_backend


class SearchConfig(AppConfig):
    name = 'mauthor.search'
    verbose_name = 'Lessons Search Config'

    def ready(self):
        metadata_updated.connect(update_index_async, dispatch_uid="metadata_updated_connect_update_index_async")
        metadata_updated_async.connect(update_index_async_from_backend, dispatch_uid="metadata_updated_async_connect_update_index_async_from_backend")

