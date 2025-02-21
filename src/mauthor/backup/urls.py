from django.conf.urls import patterns, url

urlpatterns = patterns('mauthor.backup.views',
   (r'^(?P<project_id>\d+)$', 'backup_project'),
   (r'^(?P<project_id>\d+)/select$', 'select_publications_for_backup'),
   (r'^(?P<project_id>\d+)/async/(?P<user_id>\d+)$', 'backup_project_async'),
   (r'^notify/(?P<project_backup_id>\d+)/(?P<user_id>\d+)/(?P<project_id>\d+)$', 'send_notification'),
   (r'^export_lesson/(?P<content_id>\d+)/(?P<project_backup_id>\d+)/(?P<user_id>\d+)/(?P<version>\d+)/(?P<include_player>\d+)$', 'export_lesson'),
   (r'^structure/(?P<project_id>\d+)/(?P<project_backup_id>\d+)/(?P<user_id>\d+)$', 'backup_structure'),
   (r'^restore$', 'restore_project'),
   (r'^restore/(?P<user_id>\d+)/(?P<company_id>\d+)/(?P<uploaded_file_id>\d+)$', 'restore_project_async')
)