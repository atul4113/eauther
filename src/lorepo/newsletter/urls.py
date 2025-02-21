from django.conf.urls import patterns


urlpatterns = patterns('lorepo.newsletter.views',
    (r'^$', 'index'),
    (r'^get_emails_async/(?P<newsletter_email_id>\d+)$', 'get_emails_async'),
   )