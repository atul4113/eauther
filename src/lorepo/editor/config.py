from django.apps import AppConfig
from lorepo.editor.signals import flush_addons_cache, flush_templates_cache
from lorepo.mycontent.signals import addon_deleted
from lorepo.mycontent.signals import addon_published, template_updated


class EditorConfig(AppConfig):
    name = 'lorepo.editor'
    verbose_name = 'Editor config'

    def ready(self):
        addon_published.connect(flush_addons_cache, dispatch_uid="addon_published_connect_flush_addons_cache")
        addon_deleted.connect(flush_addons_cache, dispatch_uid="addon_deleted_connect_flush_addons_cache")

        template_updated.connect(flush_templates_cache, dispatch_uid="template_updated_connect_flush_templates_cache")