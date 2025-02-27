from rest_framework import serializers

from src.lorepo.global_settings.models import GlobalSettings


class GlobalSettingsSerializer(serializers.ModelSerializer):
    referrers = serializers.DictField(child=serializers.CharField())

    class Meta:
        model = GlobalSettings
        fields = ('referrers',)
