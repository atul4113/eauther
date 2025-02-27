from django.apps import AppConfig
from src.lorepo.spaces.signals import space_access_changed, company_structure_has_changed, \
    update_company_users_space_permissions, update_user_space_permissions


class SpacesConfig(AppConfig):
    name = 'lorepo.spaces'
    verbose_name = 'Spaces Config'

    def ready(self):
        space_access_changed.connect(update_user_space_permissions, dispatch_uid='space_access_changed_connect_update_user_space_permissions')
        company_structure_has_changed.connect(update_company_users_space_permissions, dispatch_uid='company_structure_has_changed_connect_update_company_users_space_permissions')
