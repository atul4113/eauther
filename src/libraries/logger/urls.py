from django.urls import re_path
import logging
from libraries.logger import views

urlpatterns = [
    re_path(r'^fatal(/(?P<app_id>[A-Za-z0-9]{1,20})){0,1}$', views.log, {'level': logging.FATAL}),
    re_path(r'^error(/(?P<app_id>[A-Za-z0-9]{1,20})){0,1}$', views.log, {'level': logging.ERROR}),
    re_path(r'^warning(/(?P<app_id>[A-Za-z0-9]{1,20})){0,1}$', views.log, {'level': logging.WARN}),
    re_path(r'^info(/(?P<app_id>[A-Za-z0-9]{1,20})){0,1}$', views.log, {'level': logging.INFO}),
    re_path(r'^debug(/(?P<app_id>[A-Za-z0-9]{1,20})){0,1}$', views.log, {'level': logging.DEBUG}),
]
