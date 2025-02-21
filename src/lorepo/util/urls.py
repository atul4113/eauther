from django.conf.urls import patterns, url

urlpatterns = patterns('lorepo.util.views',
    (r'^object_method/(?P<module>[0-9a-zA-Z\.]+)/(?P<model>[0-9a-zA-Z]+)/(?P<method>[0-9a-zA-Z_]+)/(?P<id>\d+)$', 'object_method'),
)