from django.urls import path, re_path
from mauthor.pdfimport.views import upload, check_pdf_async
from mauthor.pdfimport.api import gce_callback, error_message_exception

urlpatterns = [
    # View URLs
    path('upload/<int:space_id>/', upload),
    path('upload/check_pdf/', check_pdf_async),
]

urlpatterns += [
    # API URLs
    re_path(r'^api/gce_callback/(?P<space_id>\d+)/(?P<user_id>\d+)/(?P<file_name>\d+)$', gce_callback),
    path('api/error_message/exception/', error_message_exception),
]
