from django.urls import path, re_path
from lorepo.public.views import view, view_addon, get_addon, full, contact_us, order_account, learn_more, \
    player, samples, content_mp, developers_mp

urlpatterns = [
    re_path(r'^view/(?P<content_id>\d+)$', view, name='view'),
    re_path(r'^view_addon/(?P<addon_id>\d+)$', view_addon, name='view_addon'),
    re_path(r'^(?P<addon_id>\w+)/getaddon$', get_addon, name='get_addon'),
    re_path(r'^full/(?P<content_id>\d+)$', full, name='full'),
    path('contact-us', contact_us, name='contact_us'),
    path('order_account', order_account, name='order_account'),
    path('learn-more', learn_more, name='learn_more'),
    path('player', player, name='player'),
    path('samples', samples, name='samples'),
    path('content_mp', content_mp, name='content_mp'),
    path('developers_mp', developers_mp, name='developers_mp'),
]
