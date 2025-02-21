from django.conf.urls import patterns, url
from .views import BasedViewRedirect

urlpatterns = patterns('mauthor.gce.views',
    (r'/', BasedViewRedirect.as_view()),
)