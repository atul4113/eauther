from django.urls import path

from src.lorepo.api.v2.home_websites.views import HomeWebsitesView

urlpatterns = [
    path('', HomeWebsitesView.as_view()),
]