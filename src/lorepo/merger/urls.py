from django.urls import re_path
from src.lorepo.merger.views import extract_pages, list_merge_pages, merge_undo, merge

urlpatterns = [
    re_path(r'^extract/(?P<content_id>\d+)/(?P<space_id>\d+)$', extract_pages),
    re_path(r'^extract/(?P<content_id>\d+)/(?P<space_id>\d+)/list', list_merge_pages),
    re_path(r'^merge_undo/$', merge_undo),
    re_path(r'^merge/(?P<space_id>\d+)$', merge),
]
