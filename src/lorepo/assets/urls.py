from django.conf.urls import patterns


urlpatterns = patterns('lorepo.assets.views',
    (r'^(?P<content_id>\d+)$', 'browse_assets'),
    (r'^upload/(?P<content_id>\d+)$', 'upload_asset'),
    (r'^rename/(?P<content_id>\d+)/(?P<href>[\w\%\/]+)$', 'rename_asset'),
    (r'^delete/(?P<content_id>\d+)/(?P<href>[\w\%\/]+)$', 'delete_assets'),
    (r'^upload_package/(?P<content_id>\d+)$', 'upload_package'),
    (r'^process_package_async/(?P<content_id>\d+)/(?P<file_id>\d+)/(?P<user_id>\d+)$', 'process_package_async'),
    (r'^replace$', 'replace'),
    (r'^replace_async/(?P<config_id>\d+)$', 'replace_async'),
    (r'^replace_page_names$', 'replace_page_names'),
    (r'^replace_page_names_async/(?P<config_id>\d+)$', 'replace_page_names_async'),
)

