from django.urls import path, re_path, include
from lorepo.api.v2.registration_api import RegisterUser, RegisterUserActivate

urlpatterns = [
    path('register', RegisterUser.as_view(), name='register'),
    path('register/activate', RegisterUserActivate.as_view(), name='register_activate'),
    path('jwt/', include('lorepo.api.v2.jwt_api')),
    path('my_content/', include('lorepo.api.v2.my_content_api')),
    path('user/', include('lorepo.api.v2.user_api')),
    path('projects/', include('lorepo.api.v2.space_api')),
    path('company/', include('lorepo.api.v2.company_api')),
    path('export/', include('lorepo.api.v2.export_api')),
    path('news/', include('lorepo.api.v2.news_api')),
    path('file/', include('lorepo.api.v2.file_api')),
    path('translations/', include('lorepo.api.v2.translations_api')),
    path('settings/', include('lorepo.api.v2.settings_api')),
    path('create_lesson/', include('lorepo.api.v2.create_lesson_api')),
    path('home_websites/', include('lorepo.api.v2.home_websites.urls')),
    path('global_settings/', include('lorepo.global_settings.urls')),
    path('newsletter/', include('lorepo.api.v2.newsletter_api')),
]
