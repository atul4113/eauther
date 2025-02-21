from django.conf.urls import patterns, url
from mauthor.bulk.views import TemplateBulkUpdate, AssetsBulkUpdate

urlpatterns = patterns('mauthor.bulk.views',
   (r'templates/(?P<project_id>\d+)$', TemplateBulkUpdate.as_view()),
   (r'assets/(?P<project_id>\d+)$', AssetsBulkUpdate.as_view()),
   (r'backend/templates/(?P<project_id>\d+)/(?P<user_id>\d+)$', TemplateBulkUpdate.as_view(run_context='backend')) ,
   (r'backend/assets/(?P<project_id>\d+)/(?P<user_id>\d+)$', AssetsBulkUpdate.as_view(run_context='backend')) ,

)