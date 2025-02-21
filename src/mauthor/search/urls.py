from django.conf.urls import patterns, url

urlpatterns = patterns('mauthor.search.views',
    (r'^put/(?P<content_id>\d+)$', 'put'),
    (r'^rebuild$', 'rebuild_search_from_date'),
    (r'^search$', 'search'),
)