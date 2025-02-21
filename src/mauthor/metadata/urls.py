from django.conf.urls import patterns, url

urlpatterns = patterns('mauthor.metadata.views',
    (r'^define$', 'define'),
    (r'^store$', 'store'),
    (r'^batch_update/(?P<company_id>\d+)/(?P<user_id>\d+)$','batch_update'),
)