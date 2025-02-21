from django.conf.urls import patterns


urlpatterns = patterns('lorepo.merger.views',
    (r'^extract/(?P<content_id>\d+)/(?P<space_id>\d+)$', 'extract_pages'),
    (r'^extract/(?P<content_id>\d+)/(?P<space_id>\d+)/list', 'list_merge_pages'),
    (r'^merge_undo/$', 'merge_undo'),
    (r'^merge/(?P<space_id>\d+)$', 'merge'),
)