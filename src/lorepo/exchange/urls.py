from django.urls import re_path
from lorepo.exchange.async_views import ExportWOMIPagesAsyncView, ExportWOMIPageAsyncView
from lorepo.exchange.models import ExportVersions
from lorepo.exchange.views import ExportWOMIPagesView, export, export_with_callback, import_presentation, list_exports, \
    create, import_presentation_async, export_async, trigger_export_async, is_lesson_created, show_exports_list

urlpatterns = [
    re_path(r'^export/(?P<content_id>\d+)/(?P<user_id>\d+)/(?P<version>\d+)$', export),
    re_path(r'^export/(?P<content_id>\d+)/(?P<user_id>\d+)/womi$', export, {'version': ExportVersions.WOMI.type}),
    re_path(r'^export_with_callback/(?P<content_id>\d+)/(?P<user_id>\d+)/(?P<version>\d+)$', export_with_callback),
    re_path(r'^import$', import_presentation),
    re_path(r'^import/(?P<space_id>\d+)$', import_presentation),
    re_path(r'^list/(?P<content_id>\d+)/womi$', list_exports, {'version': ExportVersions.WOMI.type}),
    re_path(r'^list/(?P<content_id>\d+)/(?P<version>\d+)$', list_exports),
    re_path(r'^create/(?P<content_id>\d+)$', create),
    re_path(r'^create/(?P<content_id>\d+)/(?P<version>\d+)$', create),
    re_path(r'^create/(?P<content_id>\d+)/womi$', create, {'version': ExportVersions.WOMI.type}),
    re_path(r'^import/(?P<uploaded_id>\d+)/(?P<user_id>\d+)$', import_presentation_async),
    re_path(r'^import/(?P<uploaded_id>\d+)/(?P<user_id>\d+)/(?P<space_id>\d+)$', import_presentation_async),
    re_path(r'^export_async/(?P<content_id>\d+)/(?P<session_id>[\-\w]+)$', export_async),
    re_path(r'^trigger_export_async/(?P<content_id>\d+)/(?P<session_id>[\-\w]+)/(?P<secret>\w+)$', trigger_export_async),
    re_path(r'^is_lesson_created/(?P<content_id>\d+)/(?P<session_id>[\-\w]+)/(?P<secret>\w+)$', is_lesson_created),
    re_path(r'^export/(?P<content_id>\d+)/womi/pages$', ExportWOMIPagesView.as_view(), {'start_export': False}),
    re_path(r'^export/(?P<content_id>\d+)/womi/pages/get', ExportWOMIPagesView.as_view(), {'start_export': True}),
    re_path(r'^export/(?P<womi_pages_id>\d+)/womi/pages_async$', ExportWOMIPagesAsyncView.as_view()),
    re_path(r'^export/(?P<womi_page_id>\d+)/womi/page_async$', ExportWOMIPageAsyncView.as_view()),
    re_path(r'^list/(?P<content_id>\d+)/$', show_exports_list),
]
