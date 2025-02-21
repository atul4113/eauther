from django.conf.urls import patterns


urlpatterns = patterns('lorepo.user.views',
    (r'^logout$', 'logout_view'),
    (r'^privacy$', 'privacy'),
    (r'^terms$', 'terms'),
    (r'^settings$', 'settings_view'),
    (r'^change_global_template$', 'change_global_template'),
    (r'^remove_global_template$', 'remove_global_template'),
    (r'^profile$', 'profile_view'),
    (r'^editxml$', 'edit_xml'),
    (r'^spaces/(?P<space_id>\d+)$', 'show_spaces_tree'),
    (r'^fix$', 'fix'),
    (r'^orphaned_spaces/(?P<top_level_space>\d+)$$', 'orphaned_spaces'),
    (r'trigger', 'trigger_task'),
    (r'reset_password', 'custom_reset_password'),
    (r'update_owners_permissions', 'update_owners_permissions'),
    (r'create_lessons/(?P<user_id>\d+)/(?P<space_id>\d+)/(?P<count>\d+)', 'create_lessons'),
    (r'fixlesson/(?P<content_id>\d+)$', 'fix_lesson'),
    (r'loginas/(?P<user_id>\d+)$', 'login_as')
)

