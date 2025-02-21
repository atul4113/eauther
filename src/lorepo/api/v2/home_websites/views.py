from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from libraries.utility.queues import trigger_backend_task
from lorepo.api.v2.home_websites.serializers import WebsiteSerializer, WebsiteUpdateDataSerializer
from lorepo.home.models import WebSite
from lorepo.translations.models import SupportedLanguages
from lorepo.translations.serializers import LanguagesSerializer

NUMBER_OF_VERSIONS = 2


def get_versions():
    return ['v{}'.format(i) for i in range(1, NUMBER_OF_VERSIONS + 1)]


class HomeWebsitesView(GenericAPIView):

    permission_classes = (IsAuthenticated, IsAdminUser)

    def get(self, request):
        result = []
        for language in SupportedLanguages.objects.all():
            websites = []
            for version in get_versions():
                website, _ = WebSite.objects.get_or_create(
                    version=version,
                    language=language
                )
                websites.append(WebsiteSerializer(website).data)
            result.append({
                'language': LanguagesSerializer(language).data,
                'websites': websites
            })
        return Response(result)

    def put(self, request):
        serializer = WebsiteUpdateDataSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        website = serializer.validated_data['website']
        uploaded_file = serializer.validated_data['uploaded_file']

        result = {}
        status = HTTP_200_OK

        try:
            website.validate_zipfile(uploaded_file)
            uploaded_file.save()
            website.uploaded_zip = uploaded_file
            website.status = WebSite.Status.IN_PROGRESS
            website.save()
            trigger_backend_task('/backendhome/unpack_website/{}'.format(website.pk))
        except WebSite.ZipFileException as e:
            uploaded_file.file.file.blobstore_info.delete()
            uploaded_file.delete()
            result['msg'] = e.message
            status = HTTP_400_BAD_REQUEST

        return Response(result, status)
