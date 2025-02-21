from django.conf.urls import patterns


urlpatterns = patterns('lorepo.embed.views',
    (r'^(?P<content_id>\d+)$', 'mobile'),
    (r'^(?P<content_id>\d+)/(?P<version>\d+)$', 'mobile'),
    (r'^editor/(?P<content_id>\d+)$', 'editor'),
    (r'^corporate_embed/(?P<content_id>\d+)/$', 'corporate_embed'),
    (r'^book/(?P<content_id>\d+)$', 'book'),
    (r'^iframe/(?P<content_id>\d+)$', 'iframe'),
)

