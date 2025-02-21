from rest_framework import serializers

from lorepo.home.models import WebSite
from lorepo.filestorage.models import UploadedFile


class WebsiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebSite
        fields = ('id', 'modified_date', 'version', 'status', 'language', 'url')


class WebsiteUpdateDataSerializer(serializers.Serializer):
    website = serializers.PrimaryKeyRelatedField(queryset=WebSite.objects.all())
    uploaded_file = serializers.PrimaryKeyRelatedField(queryset=UploadedFile.objects.all())
