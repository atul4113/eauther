from django.urls import re_path
from mauthor.bulk.views import TemplateBulkUpdate, AssetsBulkUpdate

urlpatterns = [
    re_path(r'templates/(?P<project_id>\d+)$', TemplateBulkUpdate.as_view(), name='template_bulk_update'),
    re_path(r'assets/(?P<project_id>\d+)$', AssetsBulkUpdate.as_view(), name='assets_bulk_update'),
    re_path(r'backend/templates/(?P<project_id>\d+)/(?P<user_id>\d+)$', TemplateBulkUpdate.as_view(), name='template_bulk_update_backend'),
    re_path(r'backend/assets/(?P<project_id>\d+)/(?P<user_id>\d+)$', AssetsBulkUpdate.as_view(), name='assets_bulk_update_backend'),
]
