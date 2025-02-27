from django.urls import path
from src.mauthor.bug_track.views import delete

urlpatterns = [
    # Correcting the URL pattern and handling the bug ID for deletion
    path('<int:bug_id>/delete/', delete, name='delete_bug'),
]
