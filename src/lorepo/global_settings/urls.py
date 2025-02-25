from django.urls import path

from lorepo.global_settings.views import GlobalSettingsView

urlpatterns = [
    path('', GlobalSettingsView.as_view()),
]