from django.urls import path, re_path, include
from django.views.generic import TemplateView
from lorepo.embed.views import present  # Import the function explicitly
from lorepo.user.views import register, custom_login  # Explicit function imports
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema')),
    path('_ah/', include('djangae.urls')),
    path('api/docs/', include('rest_framework_docs.urls')),
    path('api/v2/', include(('lorepo.api.v2.urls', 'v2'), namespace='v2')),
    # path('api/v3/', include(('mcurriculum.api.v2.urls', 'v3'), namespace='v3')),  # For Future Use
    path('cron/', include('lorepo.cron.urls')),
    path('backendhome/', include('lorepo.home.urls')),
    path('file/', include('lorepo.filestorage.urls')),
    path('user/', include('lorepo.user.urls')),
    path('assets/', include('lorepo.assets.urls')),
    path('labels/', include('lorepo.labels.urls')),
    path('doc/', include('libraries.wiki.urls')),
    path('spaces/', include('lorepo.spaces.urls')),
    path('translations/', include('lorepo.translations.urls')),
    path('accounts/register/', register),
    path('accounts/login/session/', custom_login),
    path('accounts/login/', custom_login, name='auth_login'),
    path('accounts/', include('registration.urls')),
    path('corporate/', include('lorepo.corporate.urls')),  # Should come as one of the last, overrides spaces
    path('exchange/', include('lorepo.exchange.urls')),
    path('merger/', include('lorepo.merger.urls')),
    path('newsletter/', include('lorepo.newsletter.urls')),
    path('proxy/', include('libraries.proxy.urls')),
    path('lessons_parsers/', include('mauthor.lessons_parsers.urls')),
    path('states/', include('mauthor.states.urls')),
    path('bug_track/', include('mauthor.bug_track.urls')),
    path('backup/', include('mauthor.backup.urls')),
    path('company/', include('mauthor.company.urls')),
    path('logger/', include('libraries.logger.urls')),
    path('localization/', include('mauthor.localization.urls')),
    path('exchange_narration/', include('mauthor.exchange_narration.urls')),
    path('indesign/', include('mauthor.indesign.urls')),
    path('pdfimport/', include('mauthor.pdfimport.urls')),
    path('metadata/', include('mauthor.metadata.urls')),
    path('search/', include('mauthor.search.urls')),
    path('customfixdb/', include('mauthor.customfixdb.urls')),
    path('gce/', include('mauthor.gce.urls')),

    # Regex-based URLs need re_path
    re_path(r'^mycontent/{0,1}', include('lorepo.mycontent.urls')),
    re_path(r'^public/{0,1}', include('lorepo.public.urls')),
    re_path(r'^support/{0,1}', include('lorepo.support.urls')),
    re_path(r'^editor/', include('lorepo.editor.urls')),
    re_path(r'^embed/', include('lorepo.embed.urls')),
    re_path(r'^present/(?P<content_id>\d+)$', present),
    re_path(r'^permission/{0,1}', include('lorepo.permission.urls')),
    re_path(r'^course/{0,1}', include('lorepo.course.urls')),
    re_path(r'^bulk/{0,1}', include('mauthor.bulk.urls')),

    # Static Template Views
    re_path(r'^pricing/{0,1}$', TemplateView.as_view(template_name='public/plans_and_pricing.html')),
    re_path(r'^about_us$', TemplateView.as_view(template_name='public/aboutus.html'))
]