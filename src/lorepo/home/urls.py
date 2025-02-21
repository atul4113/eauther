from django.conf.urls import patterns

urlpatterns = patterns('lorepo.home.views',
    (r'^unpack_website/(?P<website_id>\d+)$', 'unpack_website'),
)