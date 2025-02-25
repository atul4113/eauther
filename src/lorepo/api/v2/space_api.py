import logging

from django.urls import path
from django.utils.decorators import method_decorator
from lorepo.api.v2.mixins import MiddlewareMixin
from lorepo.api.v2.util import get_data_with_cursor
from lorepo.corporate.middleware import CorporateMiddleware
from lorepo.mycontent.models import Content
from lorepo.mycontent.serializers import ContentTagSerializer, SimpleContentSerializer
from lorepo.permission.decorators import has_space_access
from lorepo.permission.models import Permission
from lorepo.spaces.models import Space, UserSpacePermissions
from lorepo.spaces.serializers import SpaceSerializer, PublicationsInSpaceSerializer
from lorepo.spaces.util import structure_with_ids_as_dict
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular import views


class SpaceView(MiddlewareMixin, views.APIView):
    """
    @api {get} /api/v2/projects/ /projects/
    @apiDescription Retrieves projects
    @apiName Projects
    @apiGroup Space

    @apiHeader {String} Authorization User Token.
    @apiHeaderExample {json} Header-Example:
      {
        "Authorization": "JWT TOKEN"
      }

    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK
      [
          {
            id: 4553283809050624,
            title: "Sample Templates",
            is_locked: false,
            is_owner: false,
            is_admin: false
          },
          {
            id: 6699530506469376,
            title: "Sample Lessons",
            is_locked: false,
            is_owner: false,
            is_admin: false
          }
        ]
    """

    permission_classes = (IsAuthenticated, )
    MIDDLEWARE_CLASSES = (CorporateMiddleware, )

    def get(self, request):
        with_publications = request.GET.get('publications', False)
        context = {'request': request, 'publications': with_publications}
        return Response(SpaceSerializer(list(request.user.divisions.values()), many=True, context=context).data)


class SpaceStructure(views.APIView):
    permission_classes = (IsAuthenticated, )

    """
    @api {get} /api/v2/projects/<space_id>/structure /structure/
    @apiDescription getting space structure
    @apiName SpaceStructure
    @apiGroup Space
    @apiPermission Permission.CONTENT_VIEW
    @apiParam {boolean as ["true"|"false"]} recursive (optional) - if is set to true then it will download whole structure, if false then only one level
    @apiSampleRequest /api/v2/projects/<space_id>/structure?recursive=true example request
    @apiHeader {String} Authorization User Token.
    @apiHeaderExample {json} Header-Example:
      {
        "Authorization": "JWT TOKEN"
      }

    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK
        {
          name: "proj1",
          id: 6429669121327104,
          subspaces: [
            {
              name: "aaa",
              id: 4857985968898048
            },
            {
              name: "Publikacja1",
              id: 6113009772527616,
              subspaces: [
                {
                  name: "nowy unit",
                  id: 5255871739199488,
                  subspaces: [
                    {
                      name: "nowy unit_sub",
                      id: 6381771646042112,
                      subspaces: [
                        {
                          name: "nowy unit_sub_sub",
                          id: 4974396762488832,
                          subspaces: [
                            {
                              name: "nowy unit_sub_sub_sub",
                              id: 6100296669331456
                            }
                          ]
                        }
                      ]
                    }
                  ]
                },
                {
                  name: "6146941",
                  id: 5818821692620800
                }
              ]
            },
            {
              name: "druga",
              id: 6265360852451328
            }
          ]
        }
    """

    @method_decorator(has_space_access(Permission.CONTENT_VIEW))
    def get(self, request, space_id):
        requested_space = get_object_or_404(Space, id=space_id)

        if requested_space.is_company():
            logging.debug(space_id, requested_space, "is company level")
            raise ValidationError('Requested space is company level')

        recursive = request.GET.get('recursive', "false")
        if recursive == "true":
            recursive = True
        elif recursive == "false":
            recursive = False
        else:
            logging.debug(request, request.user, space_id, recursive)
            logging.debug(request.GET)
            raise ValidationError("GET parameters is not represented as required.")

        structure_dict = structure_with_ids_as_dict(requested_space, recursive)
        return Response(structure_dict)


class SpaceLessons(views.APIView):
    permission_classes = (IsAuthenticated, )

    """
    @api {get} /api/v2/projects/<space_id>/lessons /lessons/
    @apiDescription getting space lessons
    @apiName SpaceLessons
    @apiGroup Space
    @apiPermission Permission.CONTENT_VIEW
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
              publication_id: 6227633859723264, 
              publication_name: Publication2,
              modified_date: 1516893960000,
              icon_href: "/media/content/default_presentation.png"
            },
            {
              id: 4916741121507328,
              title: "Copy of testowy tytul",
              author: 6077825400438784,
              publication_id: 6227633859723264, 
              publication_name: Publication2,
              modified_date: 1516893960000,
              icon_href: "/media/content/default_presentation.png"
            },
            {
              id: 5214571333681152,
              title: "test",
              author: 6077825400438784,
              publication_id: 6227633859723264, 
              publication_name: Publication2,
              modified_date: 1516893960000,
              icon_href: "/media/content/default_presentation.png"
            },
            {
              id: 5355308822036480,
              title: "Copy of Copy of testowy tytul",
              author: 6077825400438784,
              publication_id: 6227633859723264,
              publication_name: Publication2,
              modified_date: 1516893960000,
              icon_href: "/media/content/default_presentation.png"
            },
            {
              id: 5425677566214144,
              title: "qewrqwrqw",
              author: 6077825400438784,
              publication_id: 6227633859723264,
              publication_name: Publication2,
              modified_date: 1516893960000,
              icon_href: "/media/content/default_presentation.png"
            }
          ],
          cursor: "CjsSNWoTZGV2fmxvcmVwb2NvcnBvcmF0ZXIeCxIRbXljb250ZW50X2NvbnRlbnQYgICAgIDU0QkMGAAgAA=="
        }
    """

    @method_decorator(has_space_access(Permission.CONTENT_VIEW))
    def get(self, request, space_id):
        requested_space = Space.objects.get(id=space_id)
        cursor = request.GET.get('cursor', None)

        if requested_space.is_company():
            raise ValidationError('Requested space is company level')

        serialized_data = get_data_with_cursor(
            query_set=Content.objects.filter(spaces=str(requested_space.id), is_deleted=False),
            cursor=cursor,
            serializer=SimpleContentSerializer,
            context={},
            batch_size=50
        )

        return Response({
            'lessons': serialized_data.data,
            'cursor': serialized_data.cursor,
            'more_count': serialized_data.more_count
        })


class PublicationsView(views.APIView):
    permission_classes = (IsAuthenticated, )
    archived = None

    """
    @api {get} /api/v2/projects/<space_id>/publications /publications/
    @apiDescription getting project publications
    @apiName ProjectPublications
    @apiGroup Space
    @apiPermission Permission.SPACE_EDIT
    @apiHeader {String} Authorization User Token.
    @apiHeaderExample {json} Header-Example:
      {
        "Authorization": "JWT TOKEN"
      }

    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK
        [
            {
                "contents_count": 3, 
                "id": 6113009772527616, 
                "parent": 6429669121327104, 
                "title": "Publikacja1"
            }, 
            {
                "contents_count": 3, 
                "id": 4857985968898048, 
                "parent": 6429669121327104, 
                "title": "aaa"
            }, 
            {
                "contents_count": 3, 
                "id": 6265360852451328, 
                "parent": 6429669121327104, 
                "title": "druga"
            }
        ]
    """

    """
    @api {get} /api/v2/projects/<space_id>/publications/archived /publications/archived
    @apiDescription getting project publications archived
    @apiName ProjectPublications
    @apiGroup Space
    @apiPermission Permission.SPACE_EDIT
    @apiHeader {String} Authorization User Token.
    @apiHeaderExample {json} Header-Example:
      {
        "Authorization": "JWT TOKEN"
      }

    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK
      [
            {
                "contents_count": 3, 
                "id": 6113009772527616, 
                "parent": 6429669121327104, 
                "title": "Publikacja1"
            }, 
            {
                "contents_count": 3, 
                "id": 4857985968898048, 
                "parent": 6429669121327104, 
                "title": "aaa"
            }, 
            {
                "contents_count": 3, 
                "id": 6265360852451328, 
                "parent": 6429669121327104, 
                "title": "druga"
            }
        ]
        
    """

    @method_decorator(has_space_access(Permission.CONTENT_VIEW))
    def get(self, request, project_id):
        project = Space.objects.get(pk=project_id)
        spaces = project.kids.filter(is_deleted=self.archived).order_by('title')
        context = {'request': request}
        return Response(PublicationsInSpaceSerializer(spaces, many=True, context=context).data)


class ProjectForPublicationView(views.APIView):
    permission_classes = (IsAuthenticated,)

    """
        @api {get} /api/v2/projects/<space_id>/get_project /<space_id>/get_project
        @apiDescription getting project of publication
        @apiName ProjectForPublications
        @apiGroup Space
        @apiPermission Permission.SPACE_EDIT
        @apiHeader {String} Authorization User Token.
        @apiHeaderExample {json} Header-Example:
          {
            "Authorization": "JWT TOKEN"
          }

        @apiSuccessExample {json} Success-Response:
          HTTP/1.1 200 OK
                {
                    "contents_count": 3, 
                    "id": 6265360852451328, 
                    "is_admin": false, 
                    "is_locked": false, 
                    "is_owner": false, 
                    "parent": 6429669121327104, 
                    "title": "druga"
                }

        """

    # @method_decorator(has_space_access(Permission.CONTENT_VIEW))
    def get(self, request, space_id):
        requested_space = Space.objects.get(id=space_id)

        division = requested_space
        while not division.is_second_level():
            division = division.parent

        context = {'request': request}
        return Response(SpaceSerializer(division, context=context).data)


class SpaceLessonTag(MiddlewareMixin, views.APIView):

    """
    @api {get} /api/v2/projects/<space_id>/lessons/<lesson_id>/tags /lessons/<lesson_id>/tags
    @apiDescription getting lesson metadata
    @apiName LessonMetadata
    @apiGroup Space
    @apiPermission Permission.CONTENT_VIEW
    @apiHeader {String} Authorization User Token.
    @apiHeaderExample {json} Header-Example:
      {
        "Authorization": "JWT TOKEN"
      }

    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK
        {
            "custom_metadata": [
                {
                    "entered_value": "warto\\u015b\\u0107 oceny",
                    "field_type_name": "short_text",
                    "name": "Ocena"
                },
                {
                    "entered_value": "zajawka",
                    "field_type_name": "long_text",
                    "name": "Zajawka"
                },
                {
                    "entered_value": "val3",
                    "field_type_name": "select",
                    "name": "Select1"
                }
            ],
            "description": "opis",
            "enable_page_metadata": false,
            "id": 5805421394657280,
            "is_template": false,
            "project": 5664683906301952,
            "score_type": "last",
            "short_description": "opis",
            "tags": "tag1",
            "title": "Copy of testowa lekcja"
        }
    """

    permission_classes = (IsAuthenticated, )
    MIDDLEWARE_CLASSES = (CorporateMiddleware,)

    @method_decorator(has_space_access(Permission.CONTENT_VIEW))
    def get(self, request, space_id, lesson_id):
        requested_space = Space.objects.get(id=space_id)

        if requested_space.is_company():
            raise ValidationError('Requested space is company level')

        lesson = Content.get_cached_or_404(lesson_id)

        context = {'space': requested_space, 'content': lesson, 'request': request}
        return Response(ContentTagSerializer(lesson, context=context).data)


class SpaceGetUsersPermissions(views.APIView):

    """
    @api {get} /api/v2/projects/permissions/<space_id>/ /permissions/<space_id>
    @apiDescription getting space permissions
    @apiName SpacePermissions
    @apiGroup Space
    @apiPermission Permission.CONTENT_VIEW
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

    permission_classes = (IsAuthenticated, )

    def get(self, request, space_id):
        usp = UserSpacePermissions.objects.get(user = request.user)
        user_permissions = Permission().get_all() if request.user.is_superuser else usp.get_permissions_for_space(space_id)

        return Response(user_permissions)



urlpatterns = [
    path('', SpaceView.as_view(), name='space'),
    path('<int:space_id>/structure', SpaceStructure.as_view(), name='space'),
    path('<int:project_id>/publications', PublicationsView.as_view(archived=False), name='publications'),
    path('<int:project_id>/publications/archived', PublicationsView.as_view(archived=True), name='publications_archived'),
    path('<int:space_id>/lessons', SpaceLessons.as_view(), name='space_lessons'),
    path('<int:space_id>/get_project', ProjectForPublicationView.as_view(), name='publication_project'),
    path('<int:space_id>/lessons/<int:lesson_id>/tags', SpaceLessonTag.as_view(), name='space_lesson_tag'),
    path('permissions/<int:space_id>', SpaceGetUsersPermissions.as_view(), name='space_permissions'),
]