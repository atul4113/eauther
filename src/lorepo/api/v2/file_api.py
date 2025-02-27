from django.urls import path
from django.http import Http404
from src.libraries.utility.helpers import blobstore_upload_url
from src.lorepo.filestorage.forms import UploadForm
from src.lorepo.filestorage.views import serve_blob
from rest_framework import views, generics
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status


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

    def get(self, request, package_id: int) -> Response:
        """Retrieve the package file."""
        return serve_blob(request, package_id)


class FileUpload(generics.GenericAPIView):
    """
    @api {get} /api/v2/file/upload /file/upload
    @apiDescription Get unique upload file url. This URL is active only for one upload operation.
        You should not append this URL to the API server URL.
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

    permission_classes = (IsAuthenticated,)

    def get(self, *args, **kwargs) -> Response:
        """Get the unique URL for file upload."""
        upload_url = blobstore_upload_url(self.request, self.request.path)
        return Response({'upload_url': upload_url})

    def post(self, *args, **kwargs) -> Response:
        """Upload a file using the unique URL."""
        my_file_form = UploadForm(self.request.POST, self.request.FILES)

        if len(self.request.FILES) > 0:
            uploaded_file = my_file_form.save(False)
            uploaded_file.owner = self.request.user
            uploaded_file.content_type = self.request.FILES['file'].content_type
            uploaded_file.filename = self.request.FILES['file'].name
            uploaded_file.save()

            return Response({'uploaded_file_id': uploaded_file.id}, status=status.HTTP_201_CREATED)
        else:
            raise ValidationError('No file provided.')

urlpatterns = [
    path('serve/<int:package_id>/', FileServeView.as_view(), name='file_serve'),
    path('upload/', FileUpload.as_view(), name='file_upload'),
]
