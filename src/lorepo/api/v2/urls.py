from django.conf.urls import patterns, url, include

from lorepo.api.v2.registration_api import RegisterUser, RegisterUserActivate

urlpatterns = patterns(
    'lorepo.api.v2',
    url(r'^register$', RegisterUser.as_view(), name='register'),
    url(r'^register/activate$', RegisterUserActivate.as_view(), name='register'),
    url(r'^jwt/', include('lorepo.api.v2.jwt_api')),
    url(r'^my_content/', include('lorepo.api.v2.my_content_api')),
    url(r'^user/', include('lorepo.api.v2.user_api')),
    url(r'^projects/', include('lorepo.api.v2.space_api')),
    url(r'^company/', include('lorepo.api.v2.company_api')),
    url(r'^export/', include('lorepo.api.v2.export_api')),
    url(r'^news/', include('lorepo.api.v2.news_api')),
    url(r'^file/', include('lorepo.api.v2.file_api')),
    url(r'^translations/', include('lorepo.api.v2.translations_api')),
    url(r'^settings/', include('lorepo.api.v2.settings_api')),
    url(r'^create_lesson/', include('lorepo.api.v2.create_lesson_api')),
    url(r'^home_websites', include('lorepo.api.v2.home_websites.urls')),
    url(r'^global_settings', include('lorepo.global_settings.urls')),
    url(r'^newsletter/', include('lorepo.api.v2.newsletter_api')),
)