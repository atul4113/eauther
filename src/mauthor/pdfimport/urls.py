from django.conf.urls import patterns, url

urlpatterns = patterns('mauthor.pdfimport.views',
    (r'^upload/(?P<space_id>\d+)$', 'upload'),
    (r'^upload/check_pdf$', 'check_pdf_async'),

)

urlpatterns += patterns('mauthor.pdfimport.api',
    (r'^api/gce_callback/(?P<space_id>\d+)/(?P<user_id>\d+)/(?P<file_name>\d+)$', 'gce_callback'),
    (r'^api/error_message/exception', 'error_message_exception'),
)