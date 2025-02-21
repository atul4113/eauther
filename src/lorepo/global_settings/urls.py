from django.conf.urls import url

from lorepo.global_settings.views import GlobalSettingsView

urlpatterns = [
    url(r'^$', GlobalSettingsView.as_view()),
]