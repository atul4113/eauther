from django.conf.urls import patterns, url


urlpatterns = patterns('mauthor.bug_track.views',
   (r'^(?P<bug_id>\d+)/delete/{0,1}$', 'delete')
)