from django.conf.urls import patterns


urlpatterns = patterns('lorepo.public.views',
    (r'^view/(?P<content_id>\d+)$', 'view'),
    (r'^view_addon/(?P<addon_id>\d+)$', 'view_addon'),
    (r'^(?P<addon_id>\w+)/getaddon$', 'get_addon'),
    (r'^full/(?P<content_id>\d+)$', 'full'),
    (r'^contact-us$', 'contact_us'),
    (r'^order_account$', 'order_account'),
    (r'^learn-more$', 'learn_more'),
    (r'^player$', 'player'),
    (r'^samples$', 'samples'),
    (r'^content_mp$', 'content_mp'),
    (r'^developers_mp$', 'developers_mp'),
)

