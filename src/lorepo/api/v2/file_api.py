from django.conf.urls import url

from libraries.utility.helpers import blobstore_upload_url
from lorepo.filestorage.forms import UploadForm
from lorepo.filestorage.views import serve_blob
from rest_framework import views, generics
from rest_framework.exceptions import ValidationError

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class FileServeView(views.APIView):
    """
    @api {get} /api/v2/file/serve/<package_id> /file/serve/<package_id>
    @apiName FileServePackageId
    @apiDescription Get Lesson package
    @apiGroup File
    @apiParam {Number} package_id (required) - lesson package id
    @apiHeader {String} Authorization User Token.
    @apiHeaderExample {json} Header-Example:
      {
        "Authorization": "JWT TOKEN"
      }
    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK
        data
    """

    permission_classes = (IsAuthenticated,)

    def get(self, request, package_id):

        return serve_blob(request, package_id)

class FileUpload(generics.GenericAPIView):
    """
        @api {get} /api/v2/file/upload /file/upload
        @apiDescription Get unique upload file url. This url is active only for one upload operation.
            You should not append this url to api server url.
        @apiName UploadFileGet
        @apiGroup File

        @apiHeader {String} Authorization User Token.
        @apiHeaderExample {json} Header-Example:
          {
            "Authorization": "JWT TOKEN"
          }

        @apiSuccessExample {json} Success-Response:
          HTTP/1.1 200 OK
          {
             "upload_url": "unique_upload_url"
          }
    """
    """
        @api {post} unique_upload_url /file/upload
        @apiDescription Upload file using upload unique url (fetched by get method on /api/v2/file/upload).
            You should send file as request payload, i.e. by submitting HTML form with file input element and
                action parameter set to unique upload url. Path to uploaded file: /file/serve/<uploaded_file_id>.
        @apiName UploadFilePost
        @apiGroup File

        @apiHeader {String} Authorization User Token.
        @apiHeaderExample {json} Header-Example:
          {
            "Authorization": "JWT TOKEN"
          }

        @apiSuccessExample {json} Success-Response:
          HTTP/1.1 200 OK
          {
             "uploaded_file_id": "6286122724360192"
          }
        @apiErrorExample {html} Error-Response:
          HTTP/1.1 404 Not Found (unique upload url is expired)
              404 Not Found
              The resource could not be found.
              No such upload session: unique_key
    """

    permission_classes = (IsAuthenticated, )

    def get(self, *args, **kwargs):
        upload_url = blobstore_upload_url(self.request, self.request.path)
        return Response({'upload_url': upload_url})

    def post(self, *args, **kwargs):
        my_file_form = UploadForm(self.request.POST, self.request.FILES)

        if len(self.request.FILES) > 0:
            uploaded_file = my_file_form.save(False)
            uploaded_file.owner = self.request.user
            uploaded_file.content_type = self.request.FILES['file'].content_type
            uploaded_file.filename = self.request.FILES['file'].name
            uploaded_file.save()

            return Response({'uploaded_file_id': uploaded_file.id})
        else:
            raise ValidationError('No file provided.')

urlpatterns = [
    url(r'^serve/(?P<package_id>\d+)$', FileServeView.as_view()),
    url(r'^upload', FileUpload.as_view()),

]