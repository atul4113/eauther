from django.urls import re_path
from lorepo.assets import views

urlpatterns = [
    re_path(r'^(?P<content_id>\d+)$', views.browse_assets),
    re_path(r'^upload/(?P<content_id>\d+)$', views.upload_asset),
    re_path(r'^rename/(?P<content_id>\d+)/(?P<href>[\w\%\/]+)$', views.rename_asset),
    re_path(r'^delete/(?P<content_id>\d+)/(?P<href>[\w\%\/]+)$', views.delete_assets),
    re_path(r'^upload_package/(?P<content_id>\d+)$', views.upload_package),
    re_path(r'^process_package_async/(?P<content_id>\d+)/(?P<file_id>\d+)/(?P<user_id>\d+)$', views.process_package_async),
    re_path(r'^replace$', views.replace),
    re_path(r'^replace_async/(?P<config_id>\d+)$', views.replace_async),
    re_path(r'^replace_page_names$', views.replace_page_names),
    re_path(r'^replace_page_names_async/(?P<config_id>\d+)$', views.replace_page_names_async),
]
