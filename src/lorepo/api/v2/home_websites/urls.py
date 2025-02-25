from django.urls import path

from lorepo.api.v2.home_websites.views import HomeWebsitesView

urlpatterns = [
    path('', HomeWebsitesView.as_view()),
]