from django.urls import path, re_path
from src.mauthor.search import views  # Import the views module

urlpatterns = [
    # Use re_path for regex-based URL patterns
    re_path(r'^put/(?P<content_id>\d+)$', views.put, name='put'),
    path('rebuild', views.rebuild_search_from_date, name='rebuild_search_from_date'),
    path('search', views.search, name='search'),
]