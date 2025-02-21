from django.conf.urls import patterns, url


urlpatterns = patterns('mauthor.indesign.views',
    (r'^upload$', 'upload'),
    (r'^upload/(?P<space_id>\d+)$', 'upload'),
    (r'^editor/(?P<file_id>\d+)$', 'editor'),
    (r'^create_lesson$', 'create_lesson'),
)