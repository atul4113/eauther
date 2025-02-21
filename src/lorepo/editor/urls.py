from django.conf.urls import patterns


urlpatterns = patterns('lorepo.editor.views',
    (r'^api/templates$', 'templates'),
    (r'^myapi/(?P<content_id>\d+)/addons$', 'addons'),
    (r'^api/feedback$', 'feedback'),
    (r'^api/addNewPage$', 'addPage'),
    (r'^api/blobUploadDir$', 'blob_upload_dir'),
)

