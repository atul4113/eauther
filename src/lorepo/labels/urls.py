from django.urls import re_path
from src.lorepo.labels import views

urlpatterns = [
    re_path(r'^$', views.index),
    re_path(r'^add$', views.addLabel),
    re_path(r'^(?P<label_id>\d+)/rename$', views.rename),
]
