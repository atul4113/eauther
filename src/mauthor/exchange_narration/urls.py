from django.urls import re_path
from src.mauthor.exchange_narration import views

urlpatterns = [
    re_path(r'^export_to_csv/(?P<content_id>\d+)/{0,1}$', views.export, {'export_type': 'csv'}),
    re_path(r'^export_to_html/(?P<content_id>\d+)/{0,1}$', views.export, {'export_type': 'html'}),
]
