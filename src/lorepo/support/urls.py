from django.urls import path, re_path
from lorepo.support.views import index, add_attachment, add_ticket, show_ticket, admin, admin_show_ticket, change_status, admin_change_status

urlpatterns = [
    path('', index, name='index'),
    re_path(r'^(?P<page>\d+)$', index, name='index_with_page'),
    path('add_attachment/<int:ticket_id>/', add_attachment, name='add_attachment'),
    path('add_attachment/<int:ticket_id>/<int:admin>/', add_attachment, name='add_attachment_with_admin'),
    path('addticket', add_ticket, name='add_ticket'),
    path('ticket/<int:ticket_id>/', show_ticket, name='show_ticket'),
    path('admin', admin, name='admin'),
    re_path(r'^admin/(?P<page>\d+)$', admin, name='admin_with_page'),
    path('admin/ticket/<int:ticket_id>/', admin_show_ticket, name='admin_show_ticket'),
    path('status/<int:ticket_id>/<int:status>/', change_status, name='change_status'),
    path('admin/status/<int:ticket_id>/<int:status>/', admin_change_status, name='admin_change_status'),
]

