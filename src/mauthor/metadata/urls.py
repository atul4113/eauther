from django.urls import path, re_path
from src.mauthor.metadata.views import define, store, batch_update

urlpatterns = [
    # View URLs
    path('define/', define),
    path('store/', store),
    re_path(r'^batch_update/(?P<company_id>\d+)/(?P<user_id>\d+)$', batch_update),
]
