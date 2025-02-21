from django.conf.urls import url

from lorepo.api.v2.home_websites.views import HomeWebsitesView

urlpatterns = [
    url(r'^$', HomeWebsitesView.as_view()),
]