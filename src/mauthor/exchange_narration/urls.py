from django.conf.urls import patterns, url, url

urlpatterns = patterns('mauthor.exchange_narration.views',
    url(r'^export_to_csv/(?P<content_id>\d+)/{0,1}$', 'export', { 'export_type' : 'csv' }),
    url(r'^export_to_html/(?P<content_id>\d+)/{0,1}$', 'export', { 'export_type' : 'html' }),
)