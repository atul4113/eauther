from django.urls import path

from . import views

urlpatterns = [
    path('api/templates', views.templates, name='templates'),
    path('myapi/<int:content_id>/addons', views.addons, name='addons'),
    path('api/feedback', views.feedback, name='feedback'),
    path('api/addNewPage', views.addPage, name='addPage'),
    path('api/blobUploadDir', views.blob_upload_dir, name='blob_upload_dir'),
]
