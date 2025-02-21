from rest_framework import serializers


class NewsletterGETSerializer(serializers.Serializer):
    is_all = serializers.BooleanField(default=False, required=False)