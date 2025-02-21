from rest_framework import serializers
from lorepo.exchange.models import ExportVersions


class PayloadExportSerializer(serializers.Serializer):
    version = serializers.IntegerField(required=True)
    session_token = serializers.CharField(required=True)
    callback_url = serializers.CharField(required=False)
    include_player = serializers.BooleanField(default=False)

    def validate_version(self, value):
        from operator import attrgetter
        ordered_versions = sorted(ExportVersions.get_exported_versions(), key=attrgetter('type'))
        version_numbers = []
        version_names = ''

        for element in ordered_versions:
            version_names += str(element[0]) + ' - ' + element[1] + '  '
            version_numbers.append(element[0])

        if value not in version_numbers:
            raise serializers.ValidationError('Wrong export version. Expected one of versions: ' + version_names)
        return value

