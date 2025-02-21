from django.conf.urls import patterns


urlpatterns = patterns('libraries.proxy.views',
    (r'^get$', 'get'),
)