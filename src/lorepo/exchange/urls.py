from django.conf.urls import patterns
from lorepo.exchange.async_views import ExportWOMIPagesAsyncView, ExportWOMIPageAsyncView
from lorepo.exchange.models import ExportVersions
from lorepo.exchange.views import ExportWOMIPagesView

urlpatterns = patterns('lorepo.exchange.views',
                       (r'^export/(?P<content_id>\d+)/(?P<user_id>\d+)/(?P<version>\d+)$', 'export'),
                       (r'^export/(?P<content_id>\d+)/(?P<user_id>\d+)/womi$', 'export', {'version': ExportVersions.WOMI.type}),
                       (r'^export_with_callback/(?P<content_id>\d+)/(?P<user_id>\d+)/(?P<version>\d+)$', 'export_with_callback'),
                       (r'^import$', 'import_presentation'),
                       (r'^import/(?P<space_id>\d+)$', 'import_presentation'),
                       (r'^list/(?P<content_id>\d+)/womi$', 'list_exports', {'version': ExportVersions.WOMI.type}),
                       (r'^list/(?P<content_id>\d+)/(?P<version>\d+)$', 'list_exports'),
                       (r'^create/(?P<content_id>\d+)$', 'create'),
                       (r'^create/(?P<content_id>\d+)/(?P<version>\d+)$', 'create'),
                       (r'^create/(?P<content_id>\d+)/womi$', 'create', {'version': ExportVersions.WOMI.type}),
                       (r'^import/(?P<uploaded_id>\d+)/(?P<user_id>\d+)$', 'import_presentation_async'),
                       (r'^import/(?P<uploaded_id>\d+)/(?P<user_id>\d+)/(?P<space_id>\d+)$', 'import_presentation_async'),
                       (r'^export_async/(?P<content_id>\d+)/(?P<session_id>[\-\w]+)$', 'export_async'),
                       (r'^trigger_export_async/(?P<content_id>\d+)/(?P<session_id>[\-\w]+)/(?P<secret>\w+)$', 'trigger_export_async'),
                       (r'^is_lesson_created/(?P<content_id>\d+)/(?P<session_id>[\-\w]+)/(?P<secret>\w+)$', 'is_lesson_created'),
                       (r'^export/(?P<content_id>\d+)/womi/pages$', ExportWOMIPagesView.as_view(), {'start_export': False}),
                       (r'^export/(?P<content_id>\d+)/womi/pages/get', ExportWOMIPagesView.as_view(), {'start_export': True}),
                       (r'^export/(?P<womi_pages_id>\d+)/womi/pages_async$', ExportWOMIPagesAsyncView.as_view()),
                       (r'^export/(?P<womi_page_id>\d+)/womi/page_async$', ExportWOMIPageAsyncView.as_view()),
                       (r'^list/(?P<content_id>\d+)/$', 'show_exports_list'),
                       )