from django.conf.urls import patterns


urlpatterns = patterns('lorepo.support.views',
    (r'^$', 'index'),
    (r'^(?P<page>\d+)$', 'index'),
    (r'^add_attachment/(?P<ticket_id>\d+)$', 'add_attachment'),
    (r'^add_attachment/(?P<ticket_id>\d+)/(?P<admin>\d)$', 'add_attachment'),
    (r'^addticket$', 'add_ticket'),
    (r'^ticket/(?P<ticket_id>\d+)$', 'show_ticket'),
    (r'^admin$', 'admin'),
    (r'^admin/(?P<page>\d+)$', 'admin'),
    (r'^admin/ticket/(?P<ticket_id>\d+)$', 'admin_show_ticket'),
    (r'^status/(?P<ticket_id>\d+)/(?P<status>\d+)$', 'change_status'),
    (r'^admin/status/(?P<ticket_id>\d+)/(?P<status>\d+)$', 'admin_change_status'),
)

