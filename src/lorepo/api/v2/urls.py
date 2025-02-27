from django.urls import path, re_path, include
from src.lorepo.api.v2.registration_api import RegisterUser, RegisterUserActivate

urlpatterns = [
    path('register', RegisterUser.as_view(), name='register'),
    path('register/activate', RegisterUserActivate.as_view(), name='register_activate'),
    path('jwt/', include('src.lorepo.api.v2.jwt_api')),
    path('my_content/', include('src.lorepo.api.v2.my_content_api')),
    path('user/', include('src.lorepo.api.v2.user_api')),
    path('projects/', include('src.lorepo.api.v2.space_api')),
    path('company/', include('src.lorepo.api.v2.company_api')),
    path('export/', include('src.lorepo.api.v2.export_api')),
    path('news/', include('src.lorepo.api.v2.news_api')),
    path('file/', include('src.lorepo.api.v2.file_api')),
    path('translations/', include('src.lorepo.api.v2.translations_api')),
    path('settings/', include('src.lorepo.api.v2.settings_api')),
    path('create_lesson/', include('src.lorepo.api.v2.create_lesson_api')),
    path('home_websites/', include('src.lorepo.api.v2.home_websites.urls')),
    path('global_settings/', include('src.lorepo.global_settings.urls')),
    path('newsletter/', include('src.lorepo.api.v2.newsletter_api')),
]
