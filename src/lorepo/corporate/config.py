from django.apps import AppConfig
from src.lorepo.corporate.signals import access_rights_changed, kids_for_space_changed, flush_kids_for_space, \
    flush_spaces_for_user, flush_company_structure_cache
from src.lorepo.corporate.signals import company_structure_changed


class CorporateConfig(AppConfig):
    name = 'lorepo.corporate'
    verbose_name = 'Corporate Config'

    def ready(self):
        company_structure_changed.connect(flush_company_structure_cache, dispatch_uid='company_structure_changed_connect_flush_company_structure_cache')
        access_rights_changed.connect(flush_spaces_for_user, dispatch_uid='access_rights_changed_connect_flush_spaces_for_user')
        kids_for_space_changed.connect(flush_kids_for_space, dispatch_uid='kids_for_space_changed_connect_flush_kids_for_space')