from django.urls import path
from django.utils.decorators import method_decorator

from src.mauthor.bug_track.models import Bug
from src.mauthor.bug_track.views import _send_emails
from rest_framework import views, status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from src.lorepo.mycontent.models import Content
from src.lorepo.mycontent.serializers import LessonBugSerializer
from src.lorepo.permission.decorators import has_space_access
from src.lorepo.permission.models import Permission


class BugsView(views.APIView):
    """
    @api {post} /api/v2/my_content/<content_id>/bugs /<content_id>/bugs
    @apiDescription Report a lesson bug
    @apiName MyContentBugtrackReport
    @apiGroup MyContent

    @apiHeader {String} Authorization User Token.
    @apiHeaderExample {json} Header-Example:
    {
        "Authorization": "JWT TOKEN"
    }

    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK
        {
          "id": 50912866630369,
          "title": "this is title",
          "description": "<p>this is description<\/p>",
          "username": "kasia",
          "created_date": "2018-03-12T09:11:56.614770"
        }
    """
    """
    @api {get} /api/v2/my_content/<content_id>/bugs /<content_id>/bugs
    @apiDescription Get all lesson bugs
    @apiName MyContentBugtrack
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
        "id": 56823929456558,
        "title": "this is title",
        "description": "<p>this is description<\/p>",
        "username": "kasia",
        "created_date": "2018-03-12T09:11:09.409410"
      }
    ]
    """

    permission_classes = (IsAuthenticated,)

    @method_decorator(has_space_access(Permission.CONTENT_VIEW))
    def post(self, request, content_id):
        content = get_object_or_404(Content, pk=content_id)
        serializer = LessonBugSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save(content=content, author=request.user)
        _send_emails(instance)
        return Response(LessonBugSerializer(instance).data)

    @method_decorator(has_space_access(Permission.CONTENT_VIEW))
    def get(self, request, content_id):
        content = get_object_or_404(Content, pk=content_id)
        bugs = Bug.objects.filter(content=content)
        return Response(LessonBugSerializer(instance=bugs, many=True).data)


class BugView(views.APIView):
    """
    @api {delete} /api/v2/my_content/<content_id>/bugs/<bug_id> /<content_id>/bugs/<bug_id>
    @apiDescription Delete a lesson bug
    @apiName MyContentBugtrackDelete
    @apiGroup MyContent

    @apiHeader {String} Authorization User Token.
    @apiHeaderExample {json} Header-Example:
    {
        "Authorization": "JWT TOKEN"
    }

    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 204 NO CONTENT
    """

    permission_classes = (IsAuthenticated,)

    @method_decorator(has_space_access(Permission.CONTENT_VIEW))
    def delete(self, request, content_id, bug_id):
        Bug.objects.filter(id=bug_id).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


urlpatterns = [
    path('', BugsView.as_view(), name='bugs'),
    path('<int:bug_id>/', BugView.as_view(), name='bug'),
]
