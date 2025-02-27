from django.urls import path, re_path
from src.lorepo.user import views

urlpatterns = [
    path('logout', views.logout_view, name='logout_view'),
    path('privacy', views.privacy, name='privacy'),
    path('terms', views.terms, name='terms'),
    path('settings', views.settings_view, name='settings_view'),
    path('change_global_template', views.change_global_template, name='change_global_template'),
    path('remove_global_template', views.remove_global_template, name='remove_global_template'),
    path('profile', views.profile_view, name='profile_view'),
    path('editxml', views.edit_xml, name='edit_xml'),
    re_path(r'^spaces/(?P<space_id>\d+)$', views.show_spaces_tree, name='show_spaces_tree'),
    path('fix', views.fix, name='fix'),
    re_path(r'^orphaned_spaces/(?P<top_level_space>\d+)$', views.orphaned_spaces, name='orphaned_spaces'),
    path('trigger', views.trigger_task, name='trigger_task'),
    path('reset_password', views.custom_reset_password, name='custom_reset_password'),
    path('update_owners_permissions', views.update_owners_permissions, name='update_owners_permissions'),
    re_path(r'^create_lessons/(?P<user_id>\d+)/(?P<space_id>\d+)/(?P<count>\d+)$', views.create_lessons, name='create_lessons'),
    re_path(r'^fixlesson/(?P<content_id>\d+)$', views.fix_lesson, name='fix_lesson'),
    re_path(r'^loginas/(?P<user_id>\d+)$', views.login_as, name='login_as'),
]
