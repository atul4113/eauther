from django.conf.urls import patterns, url

urlpatterns = patterns('mauthor.customfixdb.views',
    (r'^manage', 'manage'),
    (r'^generic_async/(?P<user_id>\d+)/(?P<page_size>\d+)/(?P<instance_name>\w+)/(?P<cursor>[\w\/\.\-=]+)/(?P<task_number>\d+)', 'generic_async'),
    (r'^generic_async/(?P<user_id>\d+)/(?P<page_size>\d+)/(?P<instance_name>\w+)', 'generic_async'),
    (r'^report/(?P<slug>\w+)', 'report'),
    )
