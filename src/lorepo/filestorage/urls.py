from django.urls import path, re_path
from lorepo.filestorage import views

urlpatterns = [
    re_path(r'^(?P<file_id>\d+)$', views.get_file, name='get_file'),
    path('upload', views.upload, name='upload'),
    path('blobUploadDir', views.blob_upload_dir, name='blob_upload_dir'),
    re_path(r'^serve/(?P<file_id>\d+)$', views.serve_blob, name='serve_blob'),
    re_path(r'^thumbnail/(?P<file_id>\d+)/(?P<width>\d+)/(?P<height>\d+)$', views.image_thumbnail, name='image_thumbnail'),
    re_path(r'^secure/(?P<file_id>\d+)$', views.serve_secure, name='serve_secure'),
    path('remove_old_gcs_async', views.remove_old_gcs_async, name='remove_old_gcs_async'),
]


