from django.conf.urls import patterns


urlpatterns = patterns('libraries.wiki.views',
    (r'^$', 'index'),
    (r'^(?P<lang_code>[A-Za-z]{2})/{0,1}$', 'index'),
    (r'^add/{0,1}$', 'addPage'),
    (r'^page$', 'index'),
    (r'^page/index$', 'pageIndex'),
    (r'^page/(?P<url>.+)$', 'index'),
    (r'^(?P<lang_code>[A-Za-z]{2})/page/(?P<url>.+)$', 'index'),
    (r'^(?P<lang_code>[A-Za-z]{2})/(?P<highlight_word>.+)/page/(?P<url>.+)$', 'index'),
    (r'^edit/(?P<page_id>\d+)$', 'edit'),
    (r'^(?P<lang_code>[A-Za-z]{2})/edit/(?P<page_id>\d+)$', 'edit'),
    (r'^upload/{0,1}$', 'upload'),
    (r'^file/{0,1}$', 'add_file'),
    (r'^preview$', 'preview_page'),
    (r'^table_of_contents', 'table_of_contents'),
    (r'^remove_from_table_of_contents', 'remove_from_toc'),
    (r'^edit_table_of_contents', 'edit_toc'),
    (r'^delete/(?P<page_id>\d+)$', 'delete'),
    (r'^fixdb_reload_wiki', 'fixdb_reload_wiki'),
)

urlpatterns += patterns('libraries.wiki.api',
    (r'^api/(?P<lang_code>[A-Za-z]{2})/page/(?P<url>.+)$', 'page'),
    (r'^api/(?P<lang_code>[A-Za-z]{2})/section/(?P<url>.+)$', 'section'),
    (r'^api/private/(?P<content_id>\d+)$', 'private_addon')
)
