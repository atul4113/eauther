from src.libraries.utility.helpers import get_object_or_none
from src.lorepo.translations.images import images_labels
from src.lorepo.translations.models import SupportedLanguages, ImportTable, TranslatedLang, TranslatedImages
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class LanguagesSerializer(serializers.ModelSerializer):

    class Meta:
        model = SupportedLanguages

    def validate(self, attrs):
        if 'lang_key' in attrs:
            lang = get_object_or_none(SupportedLanguages, lang_key=attrs['lang_key'])
            if lang is not None:
                raise ValidationError('Lang already exists')
        return attrs

    def update(self, instance, validated_data):

        allowed_fields = ['lang_key', 'lang_description']

        for field in list(validated_data.keys()):
            if field in allowed_fields:
                setattr(instance, field, validated_data.get(field))

        instance.save()

        return instance


class ImportSerializer(serializers.Serializer):
    lang = serializers.IntegerField(required=True)
    pasted_json = serializers.JSONField(required=True)
    create_notification = serializers.BooleanField(required=True)


class AddLabelSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    value = serializers.CharField(required=True)


class EditLabelSerializer(serializers.Serializer):
    lang_key = serializers.CharField(required=True)
    name = serializers.CharField(required=True)
    value = serializers.CharField(required=True)


class ImageSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = TranslatedImages

    def validate(self, attrs):
        if 'label' in attrs:
            duplicate = get_object_or_none(TranslatedImages, lang=attrs['lang'], label=attrs['label'])
            if duplicate is not None:
                raise ValidationError({'message': 'Label already exists', 'code': 0})

        if attrs['label'] not in dict(images_labels):
            raise ValidationError({'message': 'Provided label not exists in images_labels.', 'code': 1})

        return attrs

    def update(self, instance, validated_data):

        allowed_fields = ['file', 'lang', 'label']

        for field in list(validated_data.keys()):

            if field in allowed_fields:
                setattr(instance, field, validated_data.get(field))

        instance.save()

        return instance