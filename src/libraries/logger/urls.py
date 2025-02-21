from django.conf.urls import patterns
import logging

urlpatterns = patterns('libraries.logger.views',
    (r'^fatal(/(?P<app_id>[A-Za-z0-9]{1,20})){0,1}$', 'log', {'level' : logging.FATAL}),
    (r'^error(/(?P<app_id>[A-Za-z0-9]{1,20})){0,1}$', 'log', {'level' : logging.ERROR}),
    (r'^warning(/(?P<app_id>[A-Za-z0-9]{1,20})){0,1}$', 'log', {'level' : logging.WARN}),
    (r'^info(/(?P<app_id>[A-Za-z0-9]{1,20})){0,1}$', 'log', {'level' : logging.INFO}),
    (r'^debug(/(?P<app_id>[A-Za-z0-9]{1,20})){0,1}$', 'log', {'level' : logging.DEBUG})
)