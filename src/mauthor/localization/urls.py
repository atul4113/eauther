from django.urls import re_path
from mauthor.localization import views

urlpatterns = [
    re_path(r'^create_export/(?P<content_id>\d+)/{0,1}$', views.create_export),
    re_path(r'^export/(?P<content_id>\d+)/(?P<user_id>\d+)/(?P<language_code>[a-z\-]+)/{0,1}$', views.export),
    re_path(r'^import/(?P<space_id>\d+)/(?P<user_id>\d+)/(?P<uploaded_file_id>\d+)/{0,1}$', views.import_xliff),
    re_path(r'^create_import/(?P<space_id>\d+)/{0,1}$', views.create_import),
    re_path(r'^check_versions/(?P<content_id>\d+)/{0,1}$', views.check_versions),
    re_path(r'^check_repeated_ids/(?P<content_id>\d+)/{0,1}$', views.check_repeated_ids),
    re_path(r'^editor/(?P<content_id>\d+)/{0,1}$', views.editor),
    re_path(r'^close/(?P<content_id>\d+)/{0,1}$', views.close),
    re_path(r'^start_localization/(?P<content_id>\d+)/(?P<space_id>\d+)/{0,1}$', views.start_localization),
    re_path(r'^create_xliff/(?P<content_id>\d+)/(?P<project_id>\d+)/(?P<user_id>\d+)/{0,1}$', views.create_xliff),
    re_path(r'^create_xliff_trigger/(?P<content_id>\d+)/(?P<project_id>\d+)/{0,1}$', views.create_xliff_trigger),
    re_path(r'^reset_xliff_to_current/(?P<content_id>\d+)/{0,1}$', views.reset_xliff_to_current),
    re_path(r'^reset_xliff_to_original/(?P<content_id>\d+)/{0,1}$', views.reset_xliff_to_original),
    re_path(r'^show_versions/(?P<content_id>\d+)/{0,1}$', views.show_versions),
    re_path(r'^save_field/{0,1}$', views.save_field),
    re_path(r'^compare/(?P<content_id>\d+)/{0,1}$', views.compare),
    re_path(r'^get_differences/(?P<content_id>\d+)/{0,1}$', views.update_lesson),
]
