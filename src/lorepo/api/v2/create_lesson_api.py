from django.conf.urls import url
from django.utils.decorators import method_decorator
from lorepo.corporate.middleware import CorporateMiddleware
from lorepo.editor.views import _read_corporate_templates
from lorepo.filestorage.models import FileStorage
from lorepo.mycontent.models import SpaceTemplate, DefaultTemplate, Content
from lorepo.mycontent.service import add_content_to_space
from lorepo.mycontent.util import create_template_node
from lorepo.permission.decorators import has_space_access
from lorepo.permission.models import Permission
from lorepo.spaces.models import Space
from lorepo.spaces.util import get_private_space_for_user
from lorepo.token.util import create_mycontent_editor_token
from mauthor.states.models import ProjectStatesSet, ContentState
from mauthor.states.util import get_states_sets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import views
from lorepo.api.v2.mixins import MiddlewareMixin
from lorepo.mycontent.serializers import ContentSerializer, TemplateContentSerializer
from django.template.loader import render_to_string
from rest_framework import status
import datetime


class TemplateMixin:

    @method_decorator(has_space_access(Permission.CONTENT_VIEW))
    def get(self, request):
        templates = _read_corporate_templates(request)
        uri = request.build_absolute_uri("/")

        return Response({
            'content': self.serializer_class(templates, many=True).data,
        })


class TemplatesView(MiddlewareMixin, TemplateMixin, views.APIView):
    MIDDLEWARE_CLASSES = (CorporateMiddleware,)
    permission_classes = (IsAuthenticated, )
    serializer_class = ContentSerializer


class SimpleTemplatesView(MiddlewareMixin, TemplateMixin, views.APIView):
    MIDDLEWARE_CLASSES = (CorporateMiddleware,)
    permission_classes = (IsAuthenticated, )
    serializer_class = TemplateContentSerializer


class CreateLessonView(MiddlewareMixin, views.APIView):
    MIDDLEWARE_CLASSES = (CorporateMiddleware,)
    permission_classes = (IsAuthenticated, )

    @method_decorator(has_space_access(Permission.CONTENT_VIEW))
    def post(self, request):
        now = datetime.datetime.now()
        st = SpaceTemplate.objects.filter(space=request.user.company)
        dt = DefaultTemplate.objects.all()

        icon_href = None
        # Get template
        if 'templateId' in request.data and request.data['templateId']:
            template = Content.get_cached(id=request.data['templateId'])
            contents = create_template_node(template.file, request.user)
            icon_href = template.icon_href
        elif len(st) > 0:
            template = st[0].template
            contents = create_template_node(template.public_version, request.user)
            icon_href = template.icon_href
        elif len(dt) > 0:
            template = dt[0].template
            contents = create_template_node(template.file, request.user)
            icon_href = template.icon_href
        else:
            # Add empty page
            t = render_to_string('initdata/lesson/page.xml', {}).encode('utf-8')
            pageFile = FileStorage(
                created_date=now,
                modified_date=now,
                content_type="text/xml",
                contents=t,
                owner=request.user)
            pageFile.save()

            params = {'page': pageFile}
            # Add empty content file
            contents = render_to_string('initdata/lesson/content.xml', params).encode('utf-8')

        contentFile = FileStorage(
            created_date=now,
            modified_date=now,
            content_type="text/xml",
            contents=contents,
            owner=request.user)
        contentFile.version = 1
        contentFile.save()

        # Register content in database
        content = Content(
            created_date=now,
            modified_date=now,
            author=request.user,
            file=contentFile,
            icon_href=icon_href)
        content.set_metadata(request.data)
        content.add_title_to_xml()
        content.set_score_type(request.data['score_type'])
        content.save()
        contentFile.history_for = content
        contentFile.save()

        # Add connection between content and user via space
        if request.data['space_id'] is None:
            space = get_private_space_for_user(request.user)
        else:
            space = Space.objects.get(pk=request.data['space_id'])

        states_sets_dict = get_states_sets(request.user.company)
        project_states_set = ProjectStatesSet.objects.filter(project=space)
        if len(project_states_set) > 0:
            pss = project_states_set[0]
            first_state = states_sets_dict[pss.states_set][0]
            cs = ContentState(state=first_state, content=content)
            cs.is_current = True
            cs.save()
        add_content_to_space(content, space)

        token, token_key = create_mycontent_editor_token(request.user)

        return Response({
          'token': token,
          'token_key': token_key,
          'content_id': str(content.pk)
        }, status=status.HTTP_200_OK)


urlpatterns = [
    url(r'^templates$', TemplatesView.as_view(), name='templates'),
    url(r'^simpletemplates$', SimpleTemplatesView.as_view(), name='templates'),
    url(r'^create$', CreateLessonView.as_view(), name='create_lesson'),
    ]