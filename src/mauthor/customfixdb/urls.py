from django.urls import path, re_path
from src.mauthor.customfixdb.views import manage, generic_async, report

urlpatterns = [
    path('manage', manage),
    re_path(r'^generic_async/(?P<user_id>\d+)/(?P<page_size>\d+)/(?P<instance_name>\w+)/(?P<cursor>[\w\/\.\-=]+)/(?P<task_number>\d+)', generic_async),
    re_path(r'^generic_async/(?P<user_id>\d+)/(?P<page_size>\d+)/(?P<instance_name>\w+)', generic_async),
    re_path(r'^report/(?P<slug>\w+)', report),
]
