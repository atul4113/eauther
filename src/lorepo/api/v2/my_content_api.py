from djangae.contrib.pagination import Paginator
from django.urls import path, re_path, include  # ✅ Use path() or re_path()
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.contrib.auth.models import User
from src.libraries.utility.environment import get_versioned_module
from src.libraries.utility.helpers import get_object_or_none, filter_in_chunks
from src.libraries.utility.queues import trigger_backend_task
from src.lorepo.api.v2.mixins import MiddlewareMixin
from src.lorepo.api.v2.permissions.content import HasEditAssetPermission
from src.lorepo.api.v2.util import get_data_with_cursor
from src.lorepo.assets.serializers import AssetsSerializer
from src.lorepo.assets.util import update_content_assets
from src.lorepo.corporate.middleware import CorporateMiddleware
from src.lorepo.exchange.views import _trigger_creation_new
from src.lorepo.filestorage.models import FileStorage, UploadedFile
from src.lorepo.filestorage.serializers import FileStorageSerializer
from src.lorepo.merger.models import ContentMerger
from src.lorepo.mycontent.service import update_content_space, add_content_to_space
from src.lorepo.mycontent.signals import metadata_updated, addon_deleted, addon_published
from src.lorepo.mycontent.util import get_recently_opened
from src.lorepo.mycontent.lesson.update_content_template import update_content_template
from src.lorepo.mycontent.models import Content, ContentType, UpdateTemplateStatus
from src.lorepo.mycontent.serializers import ContentSerializer, SimpleContentSerializer, ContentPageMetadataSerializer, \
    ContentMetadataSerializer, ContentPageMetadataSimpleSerializer, UploadAssetsPackageSerializer
from src.lorepo.permission.decorators import has_space_access
from src.lorepo.permission.models import Permission
from src.lorepo.spaces.models import Space, SpaceType
from src.lorepo.spaces.serializers import SpaceSerializer
from src.lorepo.spaces.util import get_private_space_for_user, get_user_spaces, get_private_space_for_user_cached, \
    change_contentspace
from src.lorepo.token.util import create_mycontent_editor_token
from src.lorepo.token.util import create_mycontent_edit_addon_token
from src.mauthor.metadata.models import PageMetadata
from src.mauthor.metadata.util import copy_metadata, copy_page_metadata, get_metadata_definitions
from rest_framework.exceptions import ValidationError
from rest_framework.generics import RetrieveAPIView, get_object_or_404, GenericAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import views, mixins
from rest_framework import status
from django.shortcuts import get_object_or_404
import json
import datetime

DIRECTION_ASC = 'asc'
DIRECTION_DESC = 'desc'
MODIFIED_DATE_FIELD = 'modified_date'
TITLE_FIELD = 'title'
PAGE_SIZE = 16

class MyContentView(views.APIView):
    permission_classes = (IsAuthenticated, )
    trash = None
    """
        @api {get} /api/v2/my_content/<company_id>/lessons/trash /lessons/trash
        @apiDescription getting trash lessons
        @apiName MyContentLessonsTrash
        @apiGroup MyContent

        @apiHeader {String} Authorization User Token.
        @apiParam {String} trash (optional) - if is set then content is getting from trash
        @apiSampleRequest /api/v2/my_content/<company_id>/lessons?trash=1 example trash request
        @apiHeaderExample {json} Header-Example:
          {
            "Authorization": "JWT TOKEN"
          }

        @apiSuccessExample {json} Success-Response:
          HTTP/1.1 200 OK
            {
              more_count: 4,
              lessons: [
                {
                  id: 4581252636082176,
                  title: "dafasfas",
                  author: 6077825400438784,
                  state: null,
                  modified_date: "2017-05-12T17:44:32.084000",
                  version: "22",
                  icon_href: "/media/content/default_presentation.png"
                }
              ],
              cursor: "CjsSNWoTZGV2fmxvcmVwb2NvcnBvcmF0ZXIeCxIRbXljb250ZW50X2NvbnRlbnQYgICAgIDU0QkMGAAgAA=="
            }
        """

    """
    @api {get} /api/v2/my_content/<space_id>/lessons /lessons/
    @apiDescription getting space lessons
    @apiName MyContentLessons
    @apiGroup MyContent

    @apiHeader {String} Authorization User Token.
    @apiHeaderExample {json} Header-Example:
      {
        "Authorization": "JWT TOKEN"
      }

    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK
        {
          more_count: 4,
          lessons: [
            {
              id: 4581252636082176,
              title: "dafasfas",
              author: 6077825400438784,
              state: null,
              modified_date: "2017-05-12T17:44:32.084000",
              version: "22",
              icon_href: "/media/content/default_presentation.png"
            },
            {
              id: 4916741121507328,
              title: "Copy of testowy tytul",
              author: 6077825400438784,
              state: null,
              modified_date: "2017-05-12T14:58:06.536000",
              version: "13",
              icon_href: "/media/content/default_presentation.png"
            },
            {
              id: 5214571333681152,
              title: "test",
              author: 6077825400438784,
              state: null,
              modified_date: "2017-05-12T14:48:13.436000",
              version: "9",
              icon_href: "/media/content/default_presentation.png"
            },
            {
              id: 5355308822036480,
              title: "Copy of Copy of testowy tytul",
              author: 6077825400438784,
              state: null,
              modified_date: "2017-05-12T17:44:33.200000",
              version: "22",
              icon_href: "/media/content/default_presentation.png"
            },
            {
              id: 5425677566214144,
              title: "qewrqwrqw",
              author: 6077825400438784,
              state: null,
              modified_date: "2017-05-12T17:44:34.617000",
              version: "22",
              icon_href: "/media/content/default_presentation.png"
            }
          ],
          cursor: "CjsSNWoTZGV2fmxvcmVwb2NvcnBvcmF0ZXIeCxIRbXljb250ZW50X2NvbnRlbnQYgICAgIDU0QkMGAAgAA=="
        }
    """

    @method_decorator(has_space_access(Permission.CONTENT_VIEW))
    def get(self, request, space_id=None):

        # trash = False
        if space_id is None:
            try:
                requested_space = get_private_space_for_user(request.user)
            except :
                raise ValidationError('No private space for user %(user)s' % {'user' : request.user.username})
        else:
            # if self.trash is not None:
            #     trash = True
            # else:
            #     trash = False
            requested_space = get_object_or_404(Space, id=space_id)
            if requested_space.is_company():
                raise ValidationError('Requested space is company level')

        cursor = request.GET.get('cursor', None)

        if requested_space.is_company():
            raise ValidationError('Requested space is company level')

        serialized_data = get_data_with_cursor(
            query_set=Content.objects.filter(spaces__contains=str(requested_space.id), is_deleted=self.trash),
            cursor=cursor,
            serializer=ContentSerializer,
            context={},
            batch_size=50
        )

        return Response({
            'lessons': serialized_data.data,
            'cursor': serialized_data.cursor,
            'more_count': serialized_data.more_count
        })


class MyContentCategoriesView(views.APIView):
    permission_classes = (IsAuthenticated,)

    """
    @api {get} /api/v2/my_content/categories /categories/
    @apiDescription getting my_content categories
    @apiName MyContentCategories
    @apiGroup MyContent

    @apiHeader {String} Authorization User Token.
    @apiHeaderExample {json} Header-Example:
      {
        "Authorization": "JWT TOKEN"
      }

    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK
        [
          {
            id: 4600081772707840,
            title: "g",
            is_locked: false,
            is_owner: false,
            is_admin: false,
            parent: null,
            contents_count: 6
          },
          {
            id: 4694021297405952,
            title: "dwa",
            is_locked: false,
            is_owner: false,
            is_admin: false,
            parent: 4600081772707840,
            contents_count: 0
          },
          {
            id: 6432555339350016,
            title: "qwert",
            is_locked: false,
            is_owner: false,
            is_admin: false,
            parent: 4600081772707840,
            contents_count: 1
          },
          {
            id: 6242133669314560,
            title: "nowa",
            is_locked: false,
            is_owner: false,
            is_admin: false,
            parent: 4600081772707840,
            contents_count: 1
          }
        ]
    """

    @method_decorator(has_space_access(Permission.CONTENT_VIEW))
    def get(self, request):
        spaces = get_user_spaces(request.user)
        context = {'request': request}
        return Response(SpaceSerializer(spaces, many=True, context=context).data)


class RecentlyEditedLessonsView(views.APIView):
    permission_classes = (IsAuthenticated,)

    """
    @api {get} /api/v2/my_content/lessons/edited /lessons/edited/
    @apiDescription getting recently edited lessons
    @apiName MyContentRecentlyEditedLessons
    @apiGroup MyContent

    @apiHeader {String} Authorization User Token.
    @apiHeaderExample {json} Header-Example:
      {
        "Authorization": "JWT TOKEN"
      }

    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK
        [
            "content": [
              {
                "id": 6056110045790208,
                "title": "Copy of VLL Template",
                "author": "miotla",
                "state": null,
                "modified_date": "2017-07-10T15:00:05.413000",
                "version": "18",
                "icon_href": "/file/serve/4917015999414272",
                "is_public": true,
                "template": null,
                "file": {
                    "id": 5144752345317376,
                    "created_date": "2017-07-06T11:02:48.024000",
                    "modified_date": "2017-07-06T11:02:48.555000",
                    "owner": "miotla",
                    "version": 18,
                    "meta": "{"comment":""}"
                }
            },
              {
                "id": 6296903092273152,
                "title": "hangman",
                "author": "miotla",
                "state": null,
                "modified_date": "2017-07-03T11:23:46.875000",
                "version": "4",
                "icon_href": "/media/content/default_presentation.png",
                "is_public": false,
                "template": null,
                "file": {
                    "id": 4837026528493568,
                    "created_date": "2017-07-03T11:21:51.953000",
                    "modified_date": "2017-07-03T11:21:52.038000",
                    "owner": "miotla",
                    "version": 4,
                    "meta": "{"comment":""}"
                }
              }
            ]
        ]
    """

    @method_decorator(has_space_access(Permission.CONTENT_VIEW))
    def get(self, request):
        recently_edited_lessons = get_recently_opened(request.user)

        contents = [recently_edited_lesson.content for recently_edited_lesson in recently_edited_lessons]

        return Response({
            'content': ContentSerializer(contents, many=True).data,
        })


class ContentHistoryView(views.APIView):
    permission_classes = (IsAuthenticated,)

    """
    @api {get} /api/v2/my_content/<content_id>/history /<content_id>/history/
    @apiDescription getting lesson history
    @apiName MyContentHistory
    @apiGroup MyContent

    @apiHeader {String} Authorization User Token.
    @apiHeaderExample {json} Header-Example:
      {
        "Authorization": "JWT TOKEN"
      }

    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK
        [
            {
                "id": 5144752345317376,
                "created_date": "2017-07-06T11:02:48.024000",
                "modified_date": "2017-07-06T11:02:48.555000",
                "owner": "miotla",
                "version": 18,
                "meta": "{"comment":""}"
            },
            {
                "id": 6216776182398976,
                "created_date": "2017-07-05T09:36:02.170000",
                "modified_date": "2017-07-05T09:36:03.023000",
                "owner": "miotla",
                "version": 17,
                "meta": "{"comment":""}"
            },
            {
                "id": 5249205949956096,
                "created_date": "2017-07-05T07:21:41.724000",
                "modified_date": "2017-07-05T07:21:42.344000",
                "owner": "miotla",
                "version": 16,
                "meta": "{"comment":""}"
            }
        ]
    """

    @method_decorator(has_space_access(Permission.CONTENT_VIEW))
    def get(self, request, content_id):
        content = Content.get_cached_or_404(id=content_id)
        versions = list(content.filestorage_set.filter(content_type='text/xml').order_by('-modified_date'))
        labels = {
            'template_change': 'template replaced',
            'assets_update': 'assets updated',
            'template_update': 'template updated',
            'assets_package': 'assets package',
            'schemeless_fix': 'references to unsafe URLS updated',
            'Hierarchical Lesson report fix': 'Hierarchical Lesson report fix',  # Fix on branch test-5707m
            'property_fix_v2': 'Hierarchical Lesson report fix update',
            'property_fix_v3': 'Hierarchical Lesson report fix update',
            'properties_changer': 'Changed by properties changer'
        }
        for version in versions:
            try:
                meta = json.loads(version.meta)
                version.comment = labels[meta['comment']]
            except:
                pass

        return Response(FileStorageSerializer(versions, many=True).data)


class AssetsView(views.APIView):
    permission_classes = (IsAuthenticated,)

    """
    @api {get} /api/v2/my_content/<content_id>/assets /<content_id>/assets/
    @apiDescription getting lesson assets
    @apiName MyContentAssets
    @apiGroup MyContent

    @apiHeader {String} Authorization User Token.
    @apiHeaderExample {json} Header-Example:
      {
        "Authorization": "JWT TOKEN"
      }

    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK
        "assets": [
            {
            "href": "/file/serve/6341983069011968",
            "content_type": "image/svg+xml",
            "title": "",
            "file_name": "555001.svg"
            },
              {
            "href": "/file/serve/4934608185458688",
            "content_type": "image/png",
            "title": "",
            "file_name": "addon_advconnector.png"
            },
              {
            "href": "/file/serve/6060508092301312",
            "content_type": "image/svg+xml",
            "title": "",
            "file_name": "btn_prev.svg"
            },
        ]
    """
    """
    @api {post} /api/v2/my_content/<content_id>/assets /<content_id>/assets/
    @apiDescription updating lesson assets
    @apiName MyContentUpdateAssets
    @apiGroup MyContent

    @apiHeader {String} Authorization User Token.
    @apiHeaderExample {json} Header-Example:
      {
        "Authorization": "JWT TOKEN"
      }

    @apiSuccessExample {json} Success-Response:
    HTTP/1.1 200 OK
    {}
    """

    @method_decorator(has_space_access(Permission.CONTENT_VIEW))
    def get(self, request, content_id):
        content = Content.get_cached_or_404(id=content_id)
        content_type = request.POST.get('type', None)
        assets = content.getAssets()
        # available_types = set([asset.content_type for asset in assets])
        currently_edited = (content.who_is_editing() is not None)

        if content_type is not None and content_type != '':
            assets = [asset for asset in assets if asset.content_type == content_type]

        file_ids = [a.get_file_id() for a in assets if a is not None]
        uploaded_files = list(filter_in_chunks(UploadedFile, id__in=file_ids))
        serialized_assets = []

        for asset in assets:
            uploaded_file = None
            file_id = asset.get_file_id()

            if file_id is not None:
                uploaded_file = [uf for uf in uploaded_files if uf.id == file_id]
                if uploaded_file:
                    uploaded_file = uploaded_file[0]

            serialized_assets.append(
                AssetsSerializer(instance=asset, context={'file': uploaded_file}).data
            )

        return Response({
            'assets': serialized_assets
        })

    @method_decorator(has_space_access(Permission.ASSET_EDIT))
    def post(self, request, content_id):
        content = Content.get_cached_or_404(id=content_id)
        user = content.who_is_editing()
        confirmed = request.GET.get('confirmed', None)
        # if user and not confirmed:
        #     back = get_redirect_url(request)
        #     return render(request, 'mycontent/update_assets.html',
        #                   {
        #                       'username': user.username,
        #                       'back': back
        #                   })

        content.set_user_is_editing(request.user)
        trigger_backend_task('/mycontent/update_assets_async/%s/%s' % (content_id, request.user.id),
                             target=get_versioned_module('download'), queue_name='download')

        return Response('OK', status=status.HTTP_200_OK)


class MyContentDeleteView(MiddlewareMixin, GenericAPIView):
    MIDDLEWARE_CLASSES = (CorporateMiddleware,)
    permission_classes = (IsAuthenticated,)
    lookup_url_kwarg = 'content_id'
    queryset = Content.objects.all()

    """
    @api {delete} /api/v2/my_content/<content_id>/delete /<content_id>/delete/
    @apiDescription deleting lesson 
    @apiName MyContentDelete
    @apiGroup MyContent

    @apiHeader {String} Authorization User Token.
    @apiHeaderExample {json} Header-Example:
    {
        "Authorization": "JWT TOKEN"
    }

    @apiSuccessExample {json} Success-Response:
    HTTP/1.1 200 OK
    {}
    """

    @method_decorator(has_space_access(Permission.CONTENT_VIEW))
    def delete(self, request, content_id):
        now = datetime.datetime.now()
        content = Content.get_cached_or_404(id=content_id)
        content_space = \
        [content_space for content_space in content.contentspace_set.all() if not content_space.space.is_public()][0]
        if content_space.space.is_top_level():
            content_space.is_deleted = not content_space.is_deleted
            update_content_space(content_space)
        else:
            add_content_to_space(content, content_space.space.top_level, is_deleted=True)
            update_content_space(content_space)
            # remove_content_space(content_space)
        content.public_version = None
        content.modified_date = now
        # content.content_type = ContentType.LESSON
        content.is_deleted = not content.is_deleted
        content.save()
        metadata_updated.send(sender=None, content_id=content_id)

        if content.content_type == ContentType.ADDON:
            addon_deleted.send(sender=None, company_id=request.user.company.id)

        return Response('OK', status=status.HTTP_200_OK)


class MyContentUndeleteView(MiddlewareMixin, GenericAPIView):
    MIDDLEWARE_CLASSES = (CorporateMiddleware,)
    permission_classes = (IsAuthenticated,)
    lookup_url_kwarg = 'content_id'
    queryset = Content.objects.all()

    """
    @api {post} /api/v2/my_content/<content_id>/undelete /<content_id>/undelete/
    @apiDescription undeleting lesson 
    @apiName MyContentUnelete
    @apiGroup MyContent

    @apiHeader {String} Authorization User Token.
    @apiHeaderExample {json} Header-Example:
    {
        "Authorization": "JWT TOKEN"
    }

    @apiSuccessExample {json} Success-Response:
    HTTP/1.1 200 OK
    {}
    """

    @method_decorator(has_space_access(Permission.CONTENT_VIEW))
    def post(self, request, content_id):
        now = datetime.datetime.now()
        content = Content.get_cached_or_404(id=content_id)
        content_space = \
        [content_space for content_space in content.contentspace_set.all() if not content_space.space.is_public()][0]
        if content_space.space.is_top_level():
            content_space.is_deleted = not content_space.is_deleted
            update_content_space(content_space)
        else:
            add_content_to_space(content, content_space.space.top_level, is_deleted=True)
            update_content_space(content_space)
            # remove_content_space(content_space)
        content.public_version = None
        content.modified_date = now
        # content.content_type = ContentType.LESSON
        content.is_deleted = not content.is_deleted
        content.save()
        metadata_updated.send(sender=None, content_id=content_id)

        if content.content_type == ContentType.ADDON:
            addon_deleted.send(sender=None, company_id=request.user.company.id)

        return Response('OK', status=status.HTTP_200_OK)


class MyContentCorporateDeleteView(MiddlewareMixin, GenericAPIView):
    MIDDLEWARE_CLASSES = (CorporateMiddleware,)
    permission_classes = (IsAuthenticated,)
    lookup_url_kwarg = 'content_id'
    queryset = Content.objects.all()

    """
    @api {post} /api/v2/corporate/<content_id>/delete /corporate/<content_id>/delete/
    @apiDescription undeleting lesson 
    @apiName MyContentUnelete
    @apiGroup MyContent

    @apiHeader {String} Authorization User Token.
    @apiHeaderExample {json} Header-Example:
    {
        "Authorization": "JWT TOKEN"
    }

    @apiSuccessExample {json} Success-Response:
    HTTP/1.1 200 OK
    {}
    """

    @method_decorator(has_space_access(Permission.CONTENT_VIEW))
    def delete(self, request, content_id):
        now = datetime.datetime.now()
        content = Content.get_cached_or_404(id=content_id)
        content_space = \
        [content_space for content_space in content.contentspace_set.all() if not content_space.space.is_public()][0]
        content_space.is_deleted = not content_space.is_deleted
        update_content_space(content_space)
        content.public_version = None
        content.modified_date = now
        content.is_deleted = not content.is_deleted
        content.save()
        metadata_updated.send(sender=None, content_id=content_id)

        if content.content_type == ContentType.ADDON:
            addon_deleted.send(sender=None, company_id=request.user.company.id)

        return Response('OK', status=status.HTTP_200_OK)


class MyContentCopyView(views.APIView):
    permission_classes = (IsAuthenticated,)

    """
    @api {post} /api/v2/my_content/<content_id>/<space_id>/copy /<content_id>/<space_id>/copy/
    @apiDescription copy lesson 
    @apiName MyContentCopy
    @apiGroup MyContent

    @apiHeader {String} Authorization User Token.
    @apiHeaderExample {json} Header-Example:
    {
        "Authorization": "JWT TOKEN"
    }

    @apiSuccessExample {json} Success-Response:
    HTTP/1.1 201 CREATED
    {}
    """

    @method_decorator(has_space_access(Permission.CONTENT_VIEW))
    def post(self, request, content_id, space_id):
        if space_id is None:
            space = get_private_space_for_user(request.user)
        else:
            space = get_object_or_404(Space, id=space_id)

        content = Content.get_cached_or_404(id=content_id)
        copy = content.makeCopy(True, request.user)

        if copy.content_type != ContentType.ADDON:
            copy.add_title_to_xml()

        copy_metadata(content, copy)
        add_content_to_space(copy, space)
        metadata_updated.send(sender=None, content_id=copy.id)
        return Response('OK', status=status.HTTP_201_CREATED)


class MyContentCopyToAnotherUserView(views.APIView):
    permission_classes = (IsAuthenticated,)

    """
    @api {post} /api/v2/my_content/<content_id>/copy_to_another_user /<content_id>/copy_to_another_user/
    @apiDescription copy lesson to another user
    @apiName MyContentCopy
    @apiGroup MyContent

    @apiHeader {String} Authorization User Token.
    @apiHeaderExample {json} Header-Example:
    {
        "Authorization": "JWT TOKEN"
    }

    @apiSuccessExample {json} Success-Response:
    HTTP/1.1 201 CREATED
    {}
    """

    @method_decorator(has_space_access(Permission.CONTENT_VIEW))
    def post(self, request, content_id):

        if 'user' in request.data:
            username = request.data['user']
            try:
                user = User.objects.get(username=username)
                content = Content.get_cached(id=content_id)
                copy = content.makeCopy(True, user)
                space = get_private_space_for_user(user)
                add_content_to_space(copy, space)
                return Response('OK', status=status.HTTP_201_CREATED)
            except User.DoesNotExist:
                return Response("plain.my_lessons.panel.my_lessons.user_doesnt_exist", status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("plain.my_lessons.panel.my_lessons.please_provide_username", status=status.HTTP_400_BAD_REQUEST)

class MyContentExportView(views.APIView):
    permission_classes = (IsAuthenticated,)

    """
    @api {post} /api/v2/my_content/<content_id>/<version>/copy /<content_id>/<version>/copy/
    @apiDescription export lesson 
    @apiName MyContentExport
    @apiGroup MyContent

    @apiHeader {String} Authorization User Token.
    @apiHeaderExample {json} Header-Example:
    {
        "Authorization": "JWT TOKEN"
    }

    @apiSuccessExample {json} Success-Response:
    HTTP/1.1 200 OK
    {}
    """

    @method_decorator(has_space_access(Permission.CONTENT_VIEW))
    def post(self, request, content_id, version):
        Content.get_cached_or_404(id=content_id)
        _trigger_creation_new(request, content_id, version)

        return Response('OK', status=status.HTTP_200_OK)


class MyContentPublishView(views.APIView):
    permission_classes = (IsAuthenticated,)

    """
    @api {post} /api/v2/my_content/<content_id>/makepublic /<content_id>/makepublic/
    @apiDescription publish lesson 
    @apiName MyContentExport
    @apiGroup MyContent

    @apiHeader {String} Authorization User Token.
    @apiHeaderExample {json} Header-Example:
    {
        "Authorization": "JWT TOKEN"
    }

    @apiSuccessExample {json} Success-Response:
    HTTP/1.1 200 OK
    {}
    """
    """
    @api {delete} /api/v2/my_content/<content_id>/makepublic /<content_id>/makepublic/
    @apiDescription unpublish lesson 
    @apiName MyContentExport
    @apiGroup MyContent

    @apiHeader {String} Authorization User Token.
    @apiHeaderExample {json} Header-Example:
    {
        "Authorization": "JWT TOKEN"
    }

    @apiSuccessExample {json} Success-Response:
    HTTP/1.1 200 OK
    {}
    """
    @method_decorator(has_space_access(Permission.CONTENT_VIEW))
    def post(self, request, content_id):
        content = Content.get_cached_or_404(id=content_id)
        try:
            public_version = content.public_version
        except FileStorage.DoesNotExist:
            # public_version = None
            content.is_public = False

        # if public_version is None:
        content.is_public = True
        content.public_version = content.file

        content.save()

        if content.content_type == ContentType.ADDON:
            addon_published.send(sender=None, company_id=request.user.company.id)

        return Response('OK', status=status.HTTP_200_OK)

    @method_decorator(has_space_access(Permission.CONTENT_VIEW))
    def delete(self, request, content_id):
        content = Content.get_cached_or_404(id=content_id)

        try:
            public_version = content.public_version
        except FileStorage.DoesNotExist:
            # public_version = None
            content.is_public = False

        content.is_public = False
        content.public_version = None

        content.save()

        if content.content_type == ContentType.ADDON:
            addon_published.send(sender=None, company_id=request.user.company.id)

        return Response('OK', status=status.HTTP_204_NO_CONTENT)


class MyContentUpdateTemplateView(views.APIView):
    permission_classes = (IsAuthenticated,)

    """
    @api {post} /api/v2/my_content/<content_id>/update_template /<content_id>/update_template/
    @apiDescription updating lesson template 
    @apiName MyContentUpdateTemplate
    @apiGroup MyContent

    @apiHeader {String} Authorization User Token.
    @apiHeaderExample {json} Header-Example:
    {
        "Authorization": "JWT TOKEN"
    }

    @apiSuccessExample {json} Success-Response:
    HTTP/1.1 200 OK
    {}
    """

    @method_decorator(has_space_access(Permission.CONTENT_EDIT))
    def post(self, request, content_id):
        content = Content.get_cached_or_404(id=content_id)

        preferences = []

        for el in request.data:
            if el['value']:
                preferences.append(el['content'])

        is_updated = update_content_template(content, request.user, preferences)
        if is_updated == UpdateTemplateStatus.UPDATED:
            return Response('OK', status=status.HTTP_200_OK)
        elif is_updated == UpdateTemplateStatus.CONTENT_CURRENTLY_EDITED:
            return Response('Lesson is currently being edited.', status=status.HTTP_400_BAD_REQUEST)
        elif is_updated == UpdateTemplateStatus.TEMPLATE_CURRENTLY_EDITED:
            return Response('Template for lesson is currently being edited.', status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response('Lesson does not have associated template or the template styles are empty', status=status.HTTP_400_BAD_REQUEST)


class MyContentListMergePagesView(views.APIView):
    permission_classes = (IsAuthenticated,)

    """
    @api {get} /api/v2/my_content/<space_id>/<content_id>/page_list /<space_id>/<content_id>/page_list/
    @apiDescription getting list of pages of lesson
    @apiName MyContentGetListOfPages
    @apiGroup MyContent

    @apiHeader {String} Authorization User Token.
    @apiHeaderExample {json} Header-Example:
      {
        "Authorization": "JWT TOKEN"
      }

    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK
        "common_pages": [
          {
            "index": 2,
            "title": "Copyright"
          }
        ],
        "pages_chapters": [
              {
            "isPage": true,
            "index": 0,
            "indent": "",
            "title": "Cover Page"
            },
              {
            "isPage": false,
            "indent": "",
            "title": "Story"
            },
              {
            "isPage": true,
            "index": 1,
            "indent": "&nbsp;&nbsp;&nbsp;",
            "title": "Page 1"
            },
              {
            "isPage": true,
            "index": 2,
            "indent": "&nbsp;&nbsp;&nbsp;",
            "title": "Page 2"
            },
              {
            "isPage": true,
            "index": 3,
            "indent": "&nbsp;&nbsp;&nbsp;",
            "title": "Page 3"
            }
        ]
    """

    @method_decorator(has_space_access(Permission.CONTENT_VIEW))
    def get(self, request, content_id, space_id):
        space = get_object_or_none(Space, pk=space_id)
        content = Content.get_cached_or_404(id=content_id)
        next_url = '/mycontent'
        if space:
            if space.space_type == SpaceType.CORPORATE:
                next_url = '/corporate/list/' + space_id
            else:
                next_url = next_url + '/' + space_id
        merger = ContentMerger(content)
        pages_chapters = merger.flat_page_chapter_structure()
        common_pages = merger.common_pages()

        return Response({
            'pages_chapters': pages_chapters,
            'common_pages': common_pages
        })


class MyContentMergeView(views.APIView):
    permission_classes = (IsAuthenticated,)

    """
    @api {post} /api/v2/my_content/<space_id>/merge /<space_id>/merge/
    @apiDescription merge lessons
    @apiName MyContentMergeLessons
    @apiGroup MyContent

    @apiHeader {String} Authorization User Token.
    @apiHeaderExample {json} Header-Example:
    {
        "Authorization": "JWT TOKEN"
    }

    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK
        "content":
          {
            "id": 6056110045790208,
            "title": "Copy of VLL Template",
            "author": "miotla",
            "state": null,
            "modified_date": "2017-07-10T15:00:05.413000",
            "version": "18",
            "icon_href": "/file/serve/4917015999414272",
            "is_public": true,
            "template": null,
            "file": {
                "id": 5144752345317376,
                "created_date": "2017-07-06T11:02:48.024000",
                "modified_date": "2017-07-06T11:02:48.555000",
                "owner": "miotla",
                "version": 18,
                "meta": "{"comment":""}"
            }
        }
    """

    @method_decorator(has_space_access(Permission.CONTENT_VIEW))
    def post(self, request, space_id):
        # create merged lesson
        new_content, content_page_translated_ids = ContentMerger.create_merged_content(request.user,request.data)
        new_content.save()
        if space_id is not None:
            space = get_object_or_404(Space, pk=space_id)
        else:
            space = get_private_space_for_user(request.user)
        add_content_to_space(new_content, space, False)
        metadata_updated.send(sender=None, content_id=new_content.id)
        # copy page metadata
        for content_id, translated_ids in content_page_translated_ids:
            content_from = Content.get_cached_or_404(id=content_id)
            copy_page_metadata(content_from, new_content, translated_ids)
        request.session.pop('merge_lessons', None)
        return Response({
            'content': ContentSerializer(new_content).data,
        })


class MyContentEditLessonToken(views.APIView):
    permission_classes = (IsAuthenticated,)

    """
    @api {get} /api/v2/my_content/edit_lesson_token /edit_lesson_token/
    @apiDescription get edit lesson token
    @apiName MyContentEditLessonToken
    @apiGroup MyContent

    @apiHeader {String} Authorization User Token.
    @apiHeaderExample {json} Header-Example:
    {
        "Authorization": "JWT TOKEN"
    }

    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK
          {
            "token": "hV434",
            "token_key": "token_mycontent_editor",
        }
    """

    @method_decorator(has_space_access(Permission.CONTENT_VIEW))
    def get(self, request):
        token, token_key = create_mycontent_editor_token(request.user)
        return Response({
          'token': token,
          'token_key': token_key
        })

class MyContentEditAddonToken(views.APIView):
    permission_classes = (IsAuthenticated,)

    @method_decorator(has_space_access(Permission.CONTENT_VIEW))
    def get(self, request):
        token, token_key = create_mycontent_edit_addon_token(request.user)
        return Response({
            'token': token,
            'token_key': token_key
        })

class ContentView(views.APIView):
    permission_classes = (IsAuthenticated, )
    trash = None

    """
    @api {get} /api/v2/my_content/<space_id>/lessons_paginated /lessons/
    @apiDescription getting space lessons
    @apiName MyContentSpaceLessons
    @apiParam {String} modified_date Optional parameter, order data by modified_date,  possible values: asc, desc
    @apiParam {String} title Optional parameter, order data by title, possible values: asc, desc
    @apiParam {String} trash Optional parameter, getting data from trash or not, possible values: true, false
    @apiParam {String} page Optional parameter, possible values: true, false
    @apiGroup MyContent

    @apiHeader {String} Authorization User Token.
    @apiHeaderExample {json} Header-Example:
      {
        "Authorization": "JWT TOKEN"
      }

    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK
        {
            "lessons": [
                {
                    "author": "a", 
                    "icon_href": "/media/content/default_presentation.png", 
                    "id": 5805421394657280, 
                    "modified_date": 1516105750000, 
                    "title": "Copy of testowa lekcja"
                }
            ], 
            "more_count": -15
        }
    """
    """
    @api {get} /api/v2/my_content/lessons_paginated /lessons/
    @apiDescription getting lessons from my_content
    @apiName MyContentLessons
    @apiParam {String} modified_date Optional parameter, order data by modified_date,  possible values: asc, desc
    @apiParam {String} title Optional parameter, order data by title, possible values: asc, desc
    @apiParam {String} trash Optional parameter, getting data from trash or not, possible values: true, false
    @apiParam {String} page Optional parameter, possible values: true, false
    @apiGroup MyContent

    @apiHeader {String} Authorization User Token.
    @apiHeaderExample {json} Header-Example:
      {
        "Authorization": "JWT TOKEN"
      }

    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK
        {
            "lessons": [
                {
                    "author": "a", 
                    "icon_href": "/media/content/default_presentation.png", 
                    "id": 5805421394657280, 
                    "modified_date": 1516105750000, 
                    "title": "Copy of testowa lekcja"
                }
            ], 
            "more_count": -15
        }
    """

    @method_decorator(has_space_access(Permission.CONTENT_VIEW))
    def get(self, request, space_id=None):
        def str2bool(v):
            if isinstance(v, str) or isinstance(v, str):
                return v.lower() in ("yes", "true", "t", "1")

        order_by = MODIFIED_DATE_FIELD
        direction = '-'
        page_size = PAGE_SIZE

        modified_date = request.GET.get(MODIFIED_DATE_FIELD, None)

        if modified_date is not None and modified_date == DIRECTION_ASC:
            direction = ''
            order_by = MODIFIED_DATE_FIELD

        title = request.GET.get(TITLE_FIELD, None)

        if title is not None:
            order_by = TITLE_FIELD
            if title == DIRECTION_ASC:
                direction = ''

        page = int(request.GET.get('page', 1)) #starts from 1 not 0
        order_by = direction + order_by

        # trash = str2bool(request.GET.get('trash', 'False'))

        if space_id is None:
            try:
                requested_space = get_private_space_for_user_cached(user=request.user)
            except:
                raise ValidationError('No private space for user %(user)s' % {'user' : request.user.username})
        else:
            requested_space = Space.get_cached(space_id=space_id)

            if requested_space.is_company():
                raise ValidationError('Requested space is company level')

        if requested_space.is_company():
            raise ValidationError('Requested space is company level')

        if self.trash:
            query_set = Content.objects.filter(spaces__contains=str(requested_space.id), is_deleted=self.trash).order_by(MODIFIED_DATE_FIELD)
        else:
            query_set = Content.objects.filter(Q(content_type=1) | Q(content_type=2)).filter(spaces__contains=str(requested_space.id), is_deleted=self.trash).order_by(order_by)

        paginator = Paginator(query_set, page_size)
        contents = paginator.page(page)
        serialized_data = SimpleContentSerializer(data=contents, many=True)
        serialized_data.is_valid()

        return Response({
            'lessons': serialized_data.data,
            'more_count': paginator.count - (page_size * page)
        })


class MyContentUploadAssetPackage(CreateAPIView):
    permission_classes = (IsAuthenticated, HasEditAssetPermission)
    serializer_class = UploadAssetsPackageSerializer

    """
    @api {post} /api/v2/my_content/<content_id>/upload_asset /<content_id>/upload_asset/
    @apiDescription upload asset
    @apiName MyContentUploadAsset
    @apiGroup MyContent

    @apiHeader {String} Authorization User Token.
    @apiHeaderExample {json} Header-Example:
    {
        "Authorization": "JWT TOKEN"
    }

         
    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK
        {
        }
    """

    def perform_create(self, serializer):
        uploaded_file = get_object_or_404(UploadedFile, pk=serializer.data["fileId"])

        url = '/assets/process_package_async/{}/{}/{}'.format(self.kwargs['content_id'], uploaded_file.id, self.request.user.id)

        trigger_backend_task(url, target=get_versioned_module('download'), queue_name='download')


class MyContentUploadAsset(views.APIView):
    permission_classes = (IsAuthenticated,)

    """
    @api {post} /api/v2/my_content/<content_id>/upload_asset /<content_id>/upload_asset/
    @apiDescription upload asset
    @apiName MyContentUploadAsset
    @apiGroup MyContent

    @apiHeader {String} Authorization User Token.
    @apiHeaderExample {json} Header-Example:
    {
        "Authorization": "JWT TOKEN"
    }

    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK
          {
        }
    """

    @method_decorator(has_space_access(Permission.CONTENT_VIEW))
    def post(self, request, content_id):
        content = Content.get_cached_or_404(id=content_id)
        uploaded_file = get_object_or_404(UploadedFile, id=request.data["fileId"])
        update_content_assets(content, uploaded_file)
        return Response('OK', status=status.HTTP_200_OK)


class SingleContentView(RetrieveAPIView, mixins.UpdateModelMixin):
    """
        @api {get} /api/v2/my_content/<content_id> /<content_id>
        @apiDescription Get lesson details
        @apiName MyContentLessonDetails
        @apiGroup MyContent

        @apiHeader {String} Authorization User Token.
        @apiHeaderExample {json} Header-Example:
        {
            "Authorization": "JWT TOKEN"
        }

        @apiSuccessExample {json} Success-Response:
          HTTP/1.1 200 OK
            {
                "id": 6596520010842112,
                "title": "Lesson 1 - page 2",
                "author": "jdoe",
                "modified_date": 1519648847000,
                "project_name": "jdoe",
                "publication_name": "",
                "version": "3",
                "is_template": false,
                "enable_page_metadata": true,
                "score_type": "last",
                "content_type": 1,
                "icon_href": "/media/content/default_presentation.png",
                "is_public": false,
                "template": null,
                "file": 5620737800929280,
                "description": "long",
                "short_description": "short",
                "tags": "tags"
            }
    """

    """
        @api {put} /api/v2/my_content/<content_id> /<content_id>
        @apiDescription Update lesson details
        @apiName MyContentLessonDetailsSave
        @apiGroup MyContent

        @apiHeader {String} Authorization User Token.
        @apiHeaderExample {json} Header-Example:
        {
            "Authorization": "JWT TOKEN"
        }

        @apiParam {String} icon_id - lesson icon uploaded file id; this file can be uploaded via /api/v2/file/upload
        @apiParam {Boolean} is_template - specifies if this lesson is a template
        @apiParam {Boolean} enable_page_metadata - specifies if this lesson's pages metadata is active
        @apiParam {String} score_type - lesson score type, available options: "first", "last"
        @apiParam {String} space_id - project or publication id

        @apiParamExample {json} Request-Example:
        {
          "score_type": "last",
          "is_template": false,
          "enable_page_metadata": true,
          "icon_id": 5065621867855872,
          "space_id": 5910974510923776
        }
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = ContentSerializer
    lookup_url_kwarg = 'content_id'
    queryset = Content.objects.all()

    def get_serializer_context(self):
        ctx = {
            'details': True
        }

        if self.request.method == 'PUT':
            ctx.update({
                'icon_id': self.request.data.get('icon_id'),
                'score_type': self.request.data.get('score_type'),
            })

        return ctx

    def put(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, args, kwargs)

    # perform_update is overwritten to call change_contentspace AFTER validator was called,
    # to be sure that space_id was either integer or wasn't sent in request.params
    def perform_update(self, serializer):
        space_id = serializer.validated_data.get('space_id')
        if space_id:
            change_contentspace(serializer.instance, space_id, False)

        super(SingleContentView, self).perform_update(serializer)


class CustomMetadataDefinitionsMixin(object):

    def _get_custom_definitions(self):
        definitions = []
        company = self.request.user.company
        if company:
            definitions = get_metadata_definitions(company)
        return definitions


class ContentMetadataView(MiddlewareMixin, CustomMetadataDefinitionsMixin, GenericAPIView):
    """
        @api {get} /api/v2/my_content/<content_id>/metadata /<content_id>/metadata
        @apiDescription Get lesson metadata
        @apiName MyContentLessonMetadata
        @apiGroup MyContent

        @apiHeader {String} Authorization User Token.
        @apiHeaderExample {json} Header-Example:
        {
            "Authorization": "JWT TOKEN"
        }

        @apiSuccessExample {json} Success-Response:
          HTTP/1.1 200 OK
        {
            "id": 6597619522469888,
            "title": "Merge of Lesson 1",
            "tags": "",
            "short_description": "",
            "description": "",
            "custom_values": [
                {
                    "id": null,
                    "name": "some short text field",
                    "description": "some short text field description",
                    "value": "",
                    "order": 0,
                    "entered_value": "",
                    "is_enabled": false,
                    "field_type": 0
                },
                {
                    "id": null,
                    "name": "some long text field",
                    "description": "some long text field description",
                    "value": "",
                    "order": 1,
                    "entered_value": "",
                    "is_enabled": false,
                    "field_type": 1
                },
                {
                    "id": null,
                    "name": "some select field",
                    "description": "some select field description",
                    "value": "some,select,field,values",
                    "order": 2,
                    "entered_value": "",
                    "is_enabled": false,
                    "field_type": 2
                }
            ]
        }
    """
    """
        @api {put} /api/v2/my_content/<content_id>/metadata /<content_id>/metadata
        @apiDescription Save lesson metadata.
        @apiName MyContentLessonMetadataSave
        @apiGroup MyContent

        @apiHeader {String} Authorization User Token.
        @apiHeaderExample {json} Header-Example:
        {
            "Authorization": "JWT TOKEN"
        }

        @apiParam {String} title - lesson title
        @apiParam {String} short_description - lesson short description
        @apiParam {String} description - lesson description
        @apiParam {String} tags - lesson tags
        @apiParam {Object[]} custom_values - lesson custom metadata values

        @apiParamExample {json} Request-Example:
          {
          "title": "Lesson 1",
          "short_description": "",
          "description": "",
          "tags": "",
          "custom_values": [
            {
              "name": "some short text field",
              "description": "some short text field description",
              "value": "",
              "entered_value": "",
              "field_type": 0,
              "order": 0,
              "is_enabled": false
            },
            {
              "name": "some long text field",
              "description": "some long text field description",
              "value": "",
              "entered_value": "",
              "field_type": 1,
              "order": 1,
              "is_enabled": false
            },
            {
              "name": "some select field",
              "description": "some select field description",
              "value": "some,select,field,values",
              "entered_value": "",
              "field_type": 2,
              "order": 2,
              "is_enabled": false
            }
          ]
        }
    """

    MIDDLEWARE_CLASSES = (CorporateMiddleware,)
    permission_classes = (IsAuthenticated,)
    lookup_url_kwarg = 'content_id'
    queryset = Content.objects.all()

    @method_decorator(has_space_access(Permission.CONTENT_VIEW))
    def get(self, request, *args, **kwargs):
        content = self.get_object()

        custom_definitions = self._get_custom_definitions()

        data_serialized = ContentMetadataSerializer(
            instance=content,
            context={
                'definitions': custom_definitions
            }
        ).data

        return Response(data_serialized)

    @method_decorator(has_space_access(Permission.CONTENT_VIEW))
    def put(self, request, *args, **kwargs):
        content = self.get_object()

        custom_definitions = self._get_custom_definitions()

        serializer = ContentMetadataSerializer(
            instance=content,
            data=request.data,
            context={
                'definitions': custom_definitions,
                'custom_values': request.data.get('custom_values'),
                'company': self.request.user.company
            }
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


class ContentPagesMetadataView(MiddlewareMixin, CustomMetadataDefinitionsMixin, GenericAPIView):
    """
    @api {get} /api/v2/my_content/<content_id>/pages_metadata /<content_id>/pages_metadata
    @apiDescription Get lesson pages metadata
    @apiName MyContentPagesMetadata
    @apiGroup MyContent

    @apiHeader {String} Authorization User Token.
    @apiHeaderExample {json} Header-Example:
    {
        "Authorization": "JWT TOKEN"
    }

    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK
        [
            {
                "page_id": "6VjgxofglUac2C4D",
                "title": "Page 1",
                "tags": "page,one",
                "description": "Some page one description",
                "short_description": "Page one",
                "custom_values": [{
                    "id": 4961168263217152,
                    "name": "some short text field",
                    "description": "some short text field description",
                    "value": "",
                    "order": 0,
                    "entered_value": "Short text",
                    "is_enabled": true,
                    "field_type": 0
                }, {
                    "id": 6087068170059776,
                    "name": "long text field",
                    "description": "long text field description",
                    "value": "",
                    "order": 1,
                    "entered_value": "Long Text",
                    "is_enabled": true,
                    "field_type": 1
                }, {
                    "id": 5524118216638464,
                    "name": "some select field",
                    "description": "some select field description",
                    "value": "some,select,field,values",
                    "order": 2,
                    "entered_value": "field",
                    "is_enabled": true,
                    "field_type": 2
                }]
            }
        ]
    """
    """
        @api {put} /api/v2/my_content/<content_id>/pages_metadata /<content_id>/pages_metadata
        @apiDescription Save lesson pages metadata. Should send array of objects with params specified below.
        @apiName MyContentPagesMetadataSave
        @apiGroup MyContent

        @apiHeader {String} Authorization User Token.
        @apiHeaderExample {json} Header-Example:
        {
            "Authorization": "JWT TOKEN"
        }
        
        @apiParam {String} page_id - lesson page id
        @apiParam {String} [title] - lesson page title - readonly field
        @apiParam {String} short_description - lesson page short description
        @apiParam {String} description - lesson page description
        @apiParam {String} tags - lesson page tags
        @apiParam {Object[]} custom_values - lesson page custom metadata values
        
        @apiParamExample {json} Request-Example:
        [
          {
            "page_id": "6VjgxofglUac2C4D",
            "title": "Page 1",
            "tags": "",
            "short_description": "",
            "description": "",
            "custom_values": [
              {
                "id": null,
                "name": "some short text field",
                "description": "some short text field description",
                "value": "",
                "entered_value": "",
                "field_type": 0,
                "order": 0,
                "is_enabled": false
              },
              {
                "id": null,
                "name": "some long text field",
                "description": "some long text field description",
                "value": "",
                "entered_value": "",
                "field_type": 1,
                "order": 1,
                "is_enabled": false
              },
              {
                "id": null,
                "name": "some select field",
                "description": "some select field description",
                "value": "some,select,field,values",
                "entered_value": "",
                "field_type": 2,
                "order": 2,
                "is_enabled": false
              }
            ]
          }
        ]
    """

    MIDDLEWARE_CLASSES = (CorporateMiddleware,)
    permission_classes = (IsAuthenticated,)
    lookup_url_kwarg = 'content_id'
    queryset = Content.objects.all()

    @method_decorator(has_space_access(Permission.CONTENT_VIEW))
    def get(self, request, *args, **kwargs):
        content = self.get_object()
        pages_metadata = self._get_pages_metadata(content)
        definitions = self._get_custom_definitions()

        pages_serialized = []

        for page in pages_metadata:
            pages_serialized.append(
                ContentPageMetadataSerializer(
                    instance=page,
                    context={
                        'content': content,
                        'definitions': definitions
                    }
                ).data
            )

        return Response(pages_serialized)

    @method_decorator(has_space_access(Permission.CONTENT_VIEW))
    def put(self, request, *args, **kwargs):
        content = self.get_object()
        custom_definitions = self._get_custom_definitions()

        serializer = ContentPageMetadataSimpleSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)

        pages_ids = [page['page_id'] for page in serializer.validated_data]
        pages_metadata = list(filter_in_chunks(PageMetadata, content=content, page_id__in=pages_ids))

        serialized_data = []

        for page in serializer.validated_data:
            page_id = page['page_id']
            custom_values = page.get('custom_values')
            page_metadata = [pm for pm in pages_metadata if pm.page_id == page_id]
            if page_metadata:
                page_metadata = page_metadata[0]
            else:
                page_metadata = PageMetadata(page_id=page_id, title=page.get('title'), content=content)

            page_serializer = ContentPageMetadataSerializer(
                instance=page_metadata,
                data=page,
                context={
                    'content': content,
                    'definitions': custom_definitions,
                    'custom_values': custom_values,
                    'company': self.request.user.company
                }
            )
            page_serializer.is_valid(raise_exception=True)
            page_serializer.save()

            serialized_data.append(page_serializer.data)

        return Response(serialized_data)

    def _get_pages_metadata(self, content):
        pages_metadata = list(PageMetadata.objects.filter(content=content))
        pages = content.get_pages_data()

        all_pages_metadata = []

        for page in pages:
            page_id = page.get('id')
            page_metadata = [pm for pm in pages_metadata if pm.page_id == page_id]
            if page_metadata:
                page_metadata = page_metadata[0]
            else:
                page_metadata = PageMetadata(page_id=page_id, title=page.get('title'))
            all_pages_metadata.append(page_metadata)

        return all_pages_metadata


class MyContentSetCurrentVersion(views.APIView):
    permission_classes = (IsAuthenticated,)

    """
    @api {post} /api/v2/my_content/set_version/<content_id>/<version_id> /set_version/<content_id>/<version_id>/
    @apiDescription set version
    @apiName MyContentSetCurrentVersion
    @apiGroup MyContent

    @apiHeader {String} Authorization User Token.
    @apiHeaderExample {json} Header-Example:
    {
        "Authorization": "JWT TOKEN"
    }

    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK
          {
        }
    """

    @method_decorator(has_space_access(Permission.CONTENT_VIEW))
    def post(self, request, content_id, version_id):
        content = Content.get_cached_or_404(content_id)
        user_editing = content.who_is_editing()
        # if user_editing is not None:
            # messages.warning(request,
            #                  'Lesson is currently opened in editor by user <%s>, current version not changed.' % (
            #                  user_editing))
            # return HttpResponseRedirect('/mycontent/%s/history' % (content_id))
        file_storage = FileStorage.objects.get(pk=version_id)
        content.file = file_storage
        content.save()
        metadata_updated.send(sender=None, content_id=content_id)
        # return HttpResponseRedirect('/mycontent/%s/history' % (content_id))
        return Response('OK', status=status.HTTP_200_OK)


class MyContentFixdb(views.APIView):
    permission_classes = (IsAuthenticated,)

    @method_decorator(has_space_access(Permission.CONTENT_VIEW))
    def post(self, request, content_id):
        content = get_object_or_404(Content, pk=content_id)
        content.save()
        return Response('OK', status=status.HTTP_200_OK)


# class SingleContentView(RetrieveAPIView):
#     permission_classes = (IsAuthenticated,)
#     serializer_class = ContentSerializer
#     lookup_url_kwarg = 'content_id'
#     queryset = Content.objects.all()
#
#     """
#     @api {get} /api/v2/my_content/<content_id> /<content_id>/
#     @apiDescription getting lesson details information
#     @apiName MyContentLessonDetails
#     @apiGroup MyContent
#
#     @apiHeader {String} Authorization User Token.
#     @apiHeaderExample {json} Header-Example:
#       {
#         "Authorization": "JWT TOKEN"
#       }
#
#     @apiSuccessExample {json} Success-Response:
#       HTTP/1.1 200 OK
#         {
#             "author": "a",
#             "description": "dsafas",
#             "enable_page_metadata": false,
#             "file": 5118776383111168,
#             "icon_href": "/media/content/default_presentation.png",
#             "id": 6244676289953792,
#             "is_public": false,
#             "is_template": false,
#             "modified_date": 1516815676000,
#             "project_name": "a",
#             "publication_name": "",
#             "score_type": "last",
#             "short_description": "adsfas",
#             "tags": "dafas",
#             "template": null,
#             "title": "aaaa",
#             "version": "1"
#         }
#     """


class AddonsView(views.APIView):
    permission_classes = (IsAuthenticated, )
    trash = None

    @method_decorator(has_space_access(Permission.CONTENT_VIEW))
    def get(self, request, space_id=None):
        if space_id is None:
            try:
                requested_space = get_private_space_for_user(request.user)
            except:
                raise ValidationError('No private space for user %(user)s' % {'user': request.user.username})
        else:
            requested_space = get_object_or_404(Space, id=space_id)
            if requested_space.is_company():
                raise ValidationError('Requested space is company level')

        cursor = request.GET.get('cursor', None)

        serialized_data = get_data_with_cursor(
            query_set=Content.objects.filter(spaces__contains=str(requested_space.id), content_type=3, is_deleted=self.trash),
            cursor=cursor,
            serializer=ContentSerializer,
            context={},
            batch_size=50
        )

        return Response({
            'addons': serialized_data.data,
            'cursor': serialized_data.cursor,
            'more_count': serialized_data.more_count
        })

urlpatterns = [
    path('lessons/edited', RecentlyEditedLessonsView.as_view(), name='recently_edited_lessons'),
    path('lessons', MyContentView.as_view(trash=False), name='mycontent'),
    re_path(r'^(?P<space_id>\d+)/lessons$', MyContentView.as_view(trash=False), name='mycontent'),
    re_path(r'^(?P<space_id>\d+)/addons$', AddonsView.as_view(), name='addons'),
    path('lessons/trash', MyContentView.as_view(trash=True), name='mycontent'),
    re_path(r'^(?P<space_id>\d+)/trash$', MyContentView.as_view(trash=True), name='mycontent'),
    path('lessons_paginated', ContentView.as_view(trash=False), name='mycontent'),
    re_path(r'^(?P<space_id>\d+)/lessons_paginated$', ContentView.as_view(trash=False), name='mycontent'),
    re_path(r'^(?P<space_id>\d+)/trash_paginated$', ContentView.as_view(trash=True), name='mycontent'),
    path('categories', MyContentCategoriesView.as_view(), name='my_content_categories'),
    re_path(r'^(?P<content_id>\d+)$', SingleContentView.as_view(), name='content_details'),
    re_path(r'^(?P<content_id>\d+)/history$', ContentHistoryView.as_view(), name='content_history'),
    re_path(r'^(?P<content_id>\d+)/assets$', AssetsView.as_view(), name='assets'),
    re_path(r'^(?P<content_id>\d+)/metadata$', ContentMetadataView.as_view(), name='metadata'),
    re_path(r'^(?P<content_id>\d+)/pages_metadata$', ContentPagesMetadataView.as_view(), name='pages_metadata'),
    re_path(r'^(?P<content_id>\d+)/delete$', MyContentDeleteView.as_view(), name='content_delete'),
    re_path(r'^corporate/(?P<content_id>\d+)/delete$', MyContentCorporateDeleteView.as_view(), name='content_corporate_delete'),
    re_path(r'^(?P<content_id>\d+)/undelete$', MyContentUndeleteView.as_view(), name='content_undelete'),
    re_path(r'^(?P<content_id>\d+)/(?P<space_id>\d+)/copy$', MyContentCopyView.as_view(), name='content_copy'),
    re_path(r'^(?P<content_id>\d+)/copy_to_account$', MyContentCopyToAnotherUserView.as_view(), name='copy_to_account'),
    re_path(r'^(?P<content_id>\d+)/(?P<version>\d+)/export$', MyContentExportView.as_view(), name='content_export'),
    re_path(r'^(?P<content_id>\d+)/makepublic$', MyContentPublishView.as_view(), name='content_makepublic'),
    re_path(r'^(?P<content_id>\d+)/update_template$', MyContentUpdateTemplateView.as_view(), name='content_update_template'),
    re_path(r'^(?P<content_id>\d+)/(?P<space_id>\d+)/page_list$', MyContentListMergePagesView.as_view(), name='page_list'),
    re_path(r'^(?P<space_id>\d+)/merge$', MyContentMergeView.as_view(), name='merge'),
    path('edit_lesson_token', MyContentEditLessonToken.as_view(), name='edit_lesson_token'),
    path('edit_addon_token', MyContentEditAddonToken.as_view(), name='edit_addon_token'),
    re_path(r'^(?P<content_id>\d+)/upload_asset$', MyContentUploadAsset.as_view(), name='upload_asset'),
    re_path(r'^(?P<content_id>\d+)/upload_asset_package$', MyContentUploadAssetPackage.as_view(), name='upload_asset_package'),
    re_path(r'^set_version/(?P<content_id>\d+)/(?P<version_id>\d+)$', MyContentSetCurrentVersion.as_view(), name='set_current_version'),
    re_path(r'^(?P<content_id>\d+)/bugs', include('src.lorepo.api.v2.bugtrack_api')),
    re_path(r'^refresh_content_index/(?P<content_id>\d+)$', MyContentFixdb.as_view(), name='content_fixdb'),
]
