from django.urls import path

from src.lorepo.global_settings.views import GlobalSettingsView

urlpatterns = [
    path('', GlobalSettingsView.as_view()),
]