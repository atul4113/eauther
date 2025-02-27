from django.urls import path
from src.mauthor.backup.views import (
    backup_project,
    select_publications_for_backup,
    backup_project_async,
    send_notification,
    export_lesson,
    backup_structure,
    restore_project,
    restore_project_async
)

urlpatterns = [
    path('<int:project_id>/', backup_project, name='backup_project'),
    path('<int:project_id>/select/', select_publications_for_backup, name='select_publications_for_backup'),
    path('<int:project_id>/async/<int:user_id>/', backup_project_async, name='backup_project_async'),
    path('notify/<int:project_backup_id>/<int:user_id>/<int:project_id>/', send_notification, name='send_notification'),
    path('export_lesson/<int:content_id>/<int:project_backup_id>/<int:user_id>/<int:version>/<int:include_player>/', export_lesson, name='export_lesson'),
    path('structure/<int:project_id>/<int:project_backup_id>/<int:user_id>/', backup_structure, name='backup_structure'),
    path('restore/', restore_project, name='restore_project'),
    path('restore/<int:user_id>/<int:company_id>/<int:uploaded_file_id>/', restore_project_async, name='restore_project_async'),
]
