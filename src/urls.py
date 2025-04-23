from django.contrib import admin
from django.urls import path, re_path, include
from django.views.generic import TemplateView
from src.lorepo.embed.views import present
from src.lorepo.user.views import register, custom_login
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema')),
    path('_ah/', include('djangae.urls')),
    path('api/docs/', include('rest_framework_docs.urls')),
    path('api/v2/', include(('src.lorepo.api.v2.urls', 'v2'), namespace='v2')),
    # path('api/v3/', include(('mcurriculum.api.v2.urls', 'v3'), namespace='v3')),  # For Future Use
    # cron => few of them are working, few needs authentication,
    path('cron/', include('src.lorepo.cron.urls')),
    # required database for website ids
    path('backendhome/', include('src.lorepo.home.urls')),
    # few urls are working and few needs payload
    path('file/', include('src.lorepo.filestorage.urls')),
    # few urls are working in user section
    path('user/', include('src.lorepo.user.urls')),

    path('assets/', include('src.lorepo.assets.urls')),

    path('labels/', include('src.lorepo.labels.urls')),

    path('doc/', include('src.libraries.wiki.urls')),

    path('spaces/', include('src.lorepo.spaces.urls')),

    path('translations/', include('src.lorepo.translations.urls')),
    re_path(r'^accounts/login/session/?$', custom_login, name='custom_login'),
    re_path(r'^api/v2/accounts/login/session/?$', custom_login, name='custom_login_v2'),
    path('accounts/', include('src.registration.urls')),
    path('accounts/', include(('rest_framework_custom.urls', 'rest_framework_custom'), namespace='rest_framework_custom')),
    path('corporate/', include('src.lorepo.corporate.urls')),
    path('exchange/', include('src.lorepo.exchange.urls')),
    path('merger/', include('src.lorepo.merger.urls')),
    path('newsletter/', include('src.lorepo.newsletter.urls')),
    path('proxy/', include('src.libraries.proxy.urls')),
    path('lessons_parsers/', include('src.mauthor.lessons_parsers.urls')),
    path('states/', include('src.mauthor.states.urls')),
    path('bug_track/', include('src.mauthor.bug_track.urls')),
    path('backup/', include('src.mauthor.backup.urls')),
    path('company/', include('src.mauthor.company.urls')),
    path('logger/', include('src.libraries.logger.urls')),
    path('localization/', include('src.mauthor.localization.urls')),
    path('exchange_narration/', include('src.mauthor.exchange_narration.urls')),
    path('indesign/', include('src.mauthor.indesign.urls')),
    path('pdfimport/', include('src.mauthor.pdfimport.urls')),
    path('metadata/', include('src.mauthor.metadata.urls')),
    path('search/', include('src.mauthor.search.urls')),
    path('customfixdb/', include('src.mauthor.customfixdb.urls')),
    path('gce/', include('src.mauthor.gce.urls')),

    # Regex-based URLs need re_path
    re_path(r'^mycontent/{0,1}', include('src.lorepo.mycontent.urls')),
    re_path(r'^public/{0,1}', include('src.lorepo.public.urls')),
    re_path(r'^support/{0,1}', include('src.lorepo.support.urls')),
    re_path(r'^editor/', include('src.lorepo.editor.urls')),
    re_path(r'^embed/', include('src.lorepo.embed.urls')),
    re_path(r'^present/(?P<content_id>\d+)$', present),
    re_path(r'^permission/{0,1}', include('src.lorepo.permission.urls')),
    re_path(r'^course/{0,1}', include('src.lorepo.course.urls')),
    re_path(r'^bulk/{0,1}', include('src.mauthor.bulk.urls')),

    # Static Template Views
    re_path(r'^pricing/{0,1}$', TemplateView.as_view(template_name='public/plans_and_pricing.html')),
    re_path(r'^about_us$', TemplateView.as_view(template_name='public/aboutus.html'))
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)