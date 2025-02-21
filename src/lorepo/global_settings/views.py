from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from lorepo.global_settings.models import GlobalSettings
from lorepo.global_settings.serializers import GlobalSettingsSerializer


class GlobalSettingsView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated, IsAdminUser)
    serializer_class = GlobalSettingsSerializer

    def get_object(self):
        return GlobalSettings.load()

    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)
