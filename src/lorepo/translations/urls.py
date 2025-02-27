# Adjusted code for Django 2.0+ without patterns()

from django.urls import re_path
from src.lorepo.translations import views

urlpatterns = [
    re_path(r'^delete_lang_async/(?P<lang_id>\d+)/(?P<user_id>\d+)$', views.delete_lang_async),
    re_path(r'^add_language_async/(?P<lang_id>\d+)/(?P<user_id>\d+)$', views.add_language_async),
    re_path(r'^import/2/(?P<space_id>\d+){0,1}$', views.import_translations_step2),
    re_path(r'^import/4/(?P<space_id>\d+){0,1}$', views.import_translations_step4),
]
