import calendar
from src.lorepo.corporate.utils import get_division_for_space
import calendar
from src.libraries.utility.helpers import get_object_or_none
from src.lorepo.corporate.utils import get_division_for_space
from src.lorepo.filestorage.models import UploadedFile
from src.lorepo.mycontent.models import Content, ContentType
from src.mauthor.bug_track.models import Bug
from src.mauthor.bug_track.util import get_users_for_email
from src.mauthor.metadata.models import MetadataValue, DefinitionType, PageMetadata
from src.lorepo.spaces.util import get_space_for_content, get_space_for_content_cached
from src.mauthor.metadata.models import MetadataValue, DefinitionType
from src.mauthor.metadata.util import get_metadata_values
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer, CharField, Serializer, IntegerField
from rest_framework.serializers import ModelSerializer, ValidationError


class SimpleContentSerializer (ModelSerializer):
    modified_date = SerializerMethodField()
    icon_href = SerializerMethodField()
    author = SerializerMethodField()
    publication_name = SerializerMethodField()
    publication_id = SerializerMethodField()
    version = SerializerMethodField()
    is_deleted = SerializerMethodField()

    class Meta:
        model = Content

        fields = ('id', 'title', 'author', 'icon_href', 'modified_date', 'content_type', 'publication_name', 'publication_id',
                  'version', 'is_public', 'is_deleted')

    def get_modified_date(self, content):
        return calendar.timegm(content.modified_date.timetuple()) * 1000

    def get_publication(self, content):
        if len(content.spaces) > 1:
            return get_space_for_content_cached(content)
        else:
            return None

    def get_modified_date(self, content):
        return calendar.timegm(content.modified_date.timetuple()) * 1000

    def get_icon_href(self, content):
        if content.content_type == ContentType.ADDON:
            if content.icon_href is not None:
                return content.icon_href
            else:
                return '/media/content/default_small_addon.png'
        else:
            if content.icon_href is not None:
                return content.icon_href
            else:
                return '/media/content/default_presentation.png'

    def get_author(self, content):
        return content.author.username

    def get_version(self, content):
        return str(content.file.version)
    
    def get_is_deleted(self, content):
        return content.is_deleted

    def get_publication_name(self, content):
        publication = self.get_publication(content)
        if publication is not None:
            return publication.title

    def get_publication_id(self, content):
        publication = self.get_publication(content)
        if publication is not None:
            return publication.pk


class TemplateMixin(object):

    def get_template(self, content):
        template = None
        if content and content.content_type != ContentType.ADDON:
            template = content.get_template()
        return str(template) if template else None


class TemplateContentSerializer(TemplateMixin, ModelSerializer):
    template = SerializerMethodField()
    category = SerializerMethodField()

    class Meta:
        model = Content
        fields = ('id', 'is_public', 'template', 'title', 'category' )

    def get_category(self, content):
        return content.category


class ContentSerializer(TemplateMixin, SimpleContentSerializer):
    version = SerializerMethodField()
    project_name = SerializerMethodField()
    project_id = SerializerMethodField()
    publication_name = SerializerMethodField()
    publication_id = SerializerMethodField()
    score_type = SerializerMethodField()
    file = SerializerMethodField()
    followers = SerializerMethodField()
    is_deleted = SerializerMethodField()
    template = SerializerMethodField()
    space_id = IntegerField(allow_null=False, write_only=True, required=False)

    class Meta:
        model = Content
        fields = ('id', 'title', 'author', 'modified_date', 'project_name', 'project_id', 'publication_name', 'publication_id', 'version',
                  'is_template', 'enable_page_metadata', 'score_type', 'content_type', 'followers', 'is_deleted',
                  'icon_href', 'is_public', 'template', 'file', 'description', 'short_description', 'tags', 'space_id')

    def get_is_deleted(self, content):
        return content.is_deleted

    def get_file(self, content):
        return content.file_id

    def get_score_type(self, content):
        return content.get_score_type()

    def get_project_name(self, content):
        requested_space = get_space_for_content(content)

        if len(content.spaces) == 1:
            return requested_space.title

        division = requested_space

        while division and not division.is_second_level():
            division = division.parent

        if division:
            return division.title
        else:
            return ""

    def get_project_id(self, content):
        requested_space = get_space_for_content(content)

        if len(content.spaces) == 1:
            return requested_space.id

        division = requested_space

        while division and not division.is_second_level():
            division = division.parent

        if division:
            return division.id
        else:
            return ""

    def get_publication_name(self, content):
        if len(content.spaces) > 1:
            pub = get_space_for_content(content)
            return pub.title
        else:
            return ""

    def get_publication_id(self, content):
        if len(content.spaces) > 1:
            pub = get_space_for_content(content)
            return pub.id
        else:
            return ""

    def get_version(self, content):
        return str(content.file.version)

    def get_followers(self, content):
        space = get_space_for_content(content)
        users = get_users_for_email(space)
        return [u.username for u in users]

    def validate_title(self, value):
        if len(value) > 0:
            return value
        else:
            raise ValidationError('Title cannot be empty')

    def validate(self, data):
        if self.instance:
            icon_id = self.context.get('icon_id', None)
            if icon_id and get_object_or_none(UploadedFile, pk=icon_id):
                    data['icon_href'] = '/file/serve/' + str(icon_id)

            score_type = self.context.get('score_type', None)
            if score_type and score_type in ["first", "last"]:
                data['score_type'] = score_type

        return data

    def update(self, instance, validated_data):
        allowed_fields = ['title', 'description', 'short_description', 'tags', 'icon_href', 'is_template',
                          'enable_page_metadata', 'score_type', 'content_type']

        for field in list(validated_data.keys()):
            if field in allowed_fields:
                if field == 'score_type':
                    instance.set_score_type(validated_data.get(field))
                else:
                    setattr(instance, field, validated_data.get(field))

        instance.save()
        return instance

    def get_author(self, content):
        return content.author.username


class CustomMetadataValueSerializer(ModelSerializer):
    field_type_name = SerializerMethodField()

    class Meta:
        model = MetadataValue
        fields = ('entered_value', 'field_type_name',  'name' )

    def get_field_type_name(self, obj):
        return DefinitionType.get_name(obj.field_type)


class ContentTagSerializer (ModelSerializer):
    score_type = SerializerMethodField()
    is_template = SerializerMethodField()
    project = SerializerMethodField()
    custom_metadata = SerializerMethodField()

    class Meta:
        model = Content
        fields = ('id', 'title', 'tags', 'short_description', 'description', 'score_type', 'is_template',
                  'enable_page_metadata', 'project', 'custom_metadata')

    def get_score_type(self, obj):
        return obj.get_score_type()

    def get_is_template(self, obj):
        return obj.content_type == ContentType.TEMPLATE

    def get_project(self, obj):
        space = self.context.get('space')
        project = get_division_for_space(space)

        if project is not None:
            return project.pk
        return None

    def get_custom_metadata(self, obj):
        content = self.context.get('content')
        metadata_value = get_metadata_values(content)
        metadata_value_serializer = CustomMetadataValueSerializer(metadata_value, many=True)

        return metadata_value_serializer.data


class MetadataCustomValuesMixin(object):

    def _get_custom_values(self, content, definitions, page=None):
        if definitions:
            if page is not None and page.id is None:
                values = []
            else:
                values = MetadataValue.objects.filter(content=content, page=page).order_by('order')

            serialized_values = []
            for definition in definitions:
                value = [v for v in values if v.name == definition.name]
                if value:
                    value = value[0]
                else:
                    value = MetadataValue(
                        name=definition.name,
                        order=definition.order,
                        field_type=definition.field_type,
                        description=definition.description,
                        value=definition.value,
                        is_enabled=False
                    )

                serialized_values.append(ContentCustomMetadataValueSerializer(instance=value).data)

            return serialized_values

        return None

    def _update_custom_values(self, content, definitions, custom_values, company, page=None):
        if definitions and custom_values:
            MetadataValue.objects.filter(content=content, page=page).delete()

            for cv in custom_values:
                if cv['is_enabled']:
                    serializer = ContentCustomMetadataValueSerializer(
                        data=cv,
                        context={
                            'company': company,
                            'content': content,
                            'page': page,
                        }
                    )
                    serializer.is_valid(raise_exception=True)
                    serializer.save()


class ContentMetadataSerializer(MetadataCustomValuesMixin, ModelSerializer):
    custom_values = SerializerMethodField()
    title = CharField(required=False)

    class Meta:
        model = Content
        fields = ('id', 'title', 'tags', 'short_description', 'description', 'custom_values')

    def get_custom_values(self, content):
        definitions = self.context.get('definitions')

        return self._get_custom_values(content, definitions, None)

    def update(self, instance, validated_data):
        super(ContentMetadataSerializer, self).update(instance, validated_data)

        definitions = self.context.get('definitions')
        custom_values = self.context.get('custom_values')
        company = self.context.get('company')

        self._update_custom_values(instance, definitions, custom_values, company, None)

        return instance


class ContentCustomMetadataValueSerializer(ModelSerializer):

    class Meta:
        model = MetadataValue
        fields = ('id', 'name', 'description', 'value', 'order', 'entered_value', 'is_enabled', 'field_type')

    def validate(self, attrs):
        for name in ['company', 'content', 'page']:
            value = self.context.get(name)
            if value:
                attrs[name] = value
        return attrs


class ContentPageMetadataSimpleSerializer(Serializer):
    page_id = CharField()
    title = CharField()
    tags = CharField(required=False, allow_blank=True)
    description = CharField(required=False, allow_blank=True)
    short_description = CharField(required=False, allow_blank=True)
    custom_values = ContentCustomMetadataValueSerializer(many=True)


class ContentPageMetadataSerializer(MetadataCustomValuesMixin, ModelSerializer):
    custom_values = SerializerMethodField()

    class Meta:
        model = PageMetadata
        fields = ('page_id', 'title', 'tags', 'description', 'short_description', 'custom_values')
        read_only_fields = ('page_id', 'title')

    def get_custom_values(self, page):
        definitions = self.context.get('definitions')
        content = self.context.get('content')

        return self._get_custom_values(content, definitions, self.instance)

    def update(self, instance, validated_data):
        super(ContentPageMetadataSerializer, self).update(instance, validated_data)

        content = self.context.get('content')
        definitions = self.context.get('definitions')
        custom_values = self.context.get('custom_values')
        company = self.context.get('company')

        self._update_custom_values(content, definitions, custom_values, company, instance)

        return instance


class LessonBugSerializer(ModelSerializer):
    username = SerializerMethodField()

    class Meta:
        model = Bug
        fields = ('id', 'title', 'description', 'username', 'created_date')
        read_only_fields = ('created_date', )

    def get_username(self, bug):
        return bug.author.username


class UploadAssetsPackageSerializer(Serializer):
    fileId = IntegerField(min_value=1)
