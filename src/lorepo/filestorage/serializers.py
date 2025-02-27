from django.contrib.auth.models import User
from src.libraries.utility.helpers import get_object_or_none
from src.lorepo.filestorage.models import FileStorage
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer


class FileStorageSerializer (ModelSerializer):
    owner = SerializerMethodField()

    class Meta:
        model = FileStorage
        fields = ('id', 'created_date', 'modified_date', 'owner', 'version', 'meta')

    def get_owner(self, file_storage):
        owner = get_object_or_none(User, id=file_storage.owner.id)
        return owner.username
