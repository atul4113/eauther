import json
from django.conf.urls import url
from django.utils.decorators import method_decorator
from libraries.utility.environment import  get_versioned_module
from libraries.utility.queues import trigger_backend_task
from lorepo.corporate.models import CompanyProperties
from lorepo.exchange.serializers import PayloadExportSerializer
from lorepo.permission.decorators import has_space_access
from lorepo.permission.models import Permission
from lorepo.permission.util import get_company_for_user
from rest_framework import views
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class ExportView(views.APIView):
    permission_classes = (IsAuthenticated, )

    """
    @api {post} /api/v2/export/lesson/<content_id> /export/lesson/<content_id>
    @apiDescription exporting lessons
    @apiName ExportLesson
    @apiGroup Export
    @apiParam {Number} [version] package version 1 - SCORM_1_2, 2 - SCORM_2004, 3 - SCORM_XAPI'
    @apiParam {String} [session_token] session token (random string) resend with callback
    @apiParam {String} [callback_url] Optional url address to send information about export status
    @apiParam {Boolean} [include_player] Optional should include player
    @apiParamExample {json} Request-Example:
                 { 
                 "version": "1",
                 "session_token": "qwerty",
                 "callback_url": "http://example.com/export_confirm",
                 "include_player": "False"
                 }

    @apiHeader {String} Authorization User Token.
    @apiHeaderExample {json} Header-Example:
      {
        "Authorization": "JWT TOKEN"
      }

    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK

    """

    @method_decorator(has_space_access(Permission.EXCHANGE_EXPORT))
    def post(self, request, content_id, *args, **kwargs):
        payload = self.request.data
        if payload is None:
            raise ValidationError('No payload provided.')

        serializer = PayloadExportSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        payload = serializer.validated_data
        version = payload.get('version')
        session_token = payload.get('session_token')
        include_player = payload.get('include_player', False)
        callback_url = payload.get('callback_url', None)

        if callback_url is None:
            trigger_backend_task("/exchange/export/%(content_id)s/%(user_id)s/%(version)s" % {
                'content_id': content_id,
                'user_id': self.request.user.id,
                'version': version
            }, target=get_versioned_module(module_name='download'), queue_name='download')

            return Response({})

        company = get_company_for_user(self.request.user)
        companyproperties = CompanyProperties.objects.get(company=company)

        if hasattr(companyproperties, 'callback_url') and companyproperties.callback_url is not None:
            callback_url_company = companyproperties.callback_url
            if callback_url_company != callback_url:
                raise ValidationError('Provided callback_url is not the same as company callback_url')

            trigger_backend_task("/exchange/export_with_callback/%(content_id)s/%(user_id)s/%(version)s" % {
                'content_id': content_id,
                'user_id': self.request.user.id,
                'version': version}, target=get_versioned_module(module_name='download'),
                                 payload=json.dumps({'callback_url': callback_url, 'session_token': session_token, 'include_player': include_player}), queue_name='download')

        return Response({})


# class ExportTestView(views.APIView):
#

#     def post(self, request, *args, **kwargs):
#         payload = self.request.data
#         import logging
#         logging.error('payload') #this class is for tests purposes, the same urls should implement client
#         logging.error(payload)
#
#         return Response({})
#
#
#     def get(self, request, *args, **kwargs):
#         return Response({})

urlpatterns = [
    url(r'^lesson/(?P<content_id>\d+)$', ExportView.as_view(), name='export'),
    # url(r'^callback_test$', ExportTestView.as_view(), name='callback_test'),
    ]