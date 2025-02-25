from django.urls import path
from mauthor.indesign.views import upload, editor, create_lesson

urlpatterns = [
    path('upload/', upload),
    path('upload/<int:space_id>/', upload),
    path('editor/<int:file_id>/', editor),
    path('create_lesson/', create_lesson),
]
