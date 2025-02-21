from django.conf.urls import patterns


urlpatterns = patterns('lorepo.filestorage.views',
    (r'^(?P<file_id>\d+)$', 'get_file'),
    (r'^upload$', 'upload'),
    (r'^blobUploadDir$', 'blob_upload_dir'),
    (r'^serve/(?P<file_id>\d+)$', 'serve_blob'),
    (r'^thumbnail/(?P<file_id>\d+)/(?P<width>\d+)/(?P<height>\d+)$', 'image_thumbnail'),
    (r'^secure/(?P<file_id>\d+)$', 'serve_secure'),
    (r'remove_old_gcs_async$', 'remove_old_gcs_async')
)

