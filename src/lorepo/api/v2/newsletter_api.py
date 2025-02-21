import time
from django.conf.urls import url

from lorepo.newsletter.serializers import NewsletterGETSerializer
from lorepo.newsletter.utils import NewsletterEmailProcessor
from rest_framework import views
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
import libraries.utility.cacheproxy as cache


class EmailsView(views.APIView):
    permission_classes = (IsAdminUser,)

    """
    @api {get} /api/v2/newsletter/emails /emails
    @apiDescription Get users emails. Data are sent on user email.
    @apiName NewsletterEmails
    @apiGroup Newsletter
    @apiPermission SuperAdmin
    @apiParam {Boolean} [is_all] {optional} Optional parameter to getting all emails
    @apiHeader {String} Authorization User Token.
    @apiHeaderExample {json} Header-Example:
      {
        "Authorization": "JWT TOKEN"
      }

    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK
      {
        "code":1,
        "message":"Task scheduled correctly. Please wait for an email."
      }

    """
    def get(self, request):

        serializer = NewsletterGETSerializer(data=self.request.GET)
        serializer.is_valid(raise_exception=True)
        is_all = serializer.validated_data["is_all"]

        timestamp = int(time.time())

        if is_all:
            response = NewsletterEmailProcessor.process_all_mode(request, timestamp, is_all)
            return Response(response)

        newsletter_emails_all_count_cached = cache.get("newsletter_emails_all_count")

        if newsletter_emails_all_count_cached is None:
            result = NewsletterEmailProcessor.process_all_count_not_cached(request, timestamp)
            return Response(result)

        result = NewsletterEmailProcessor.process_in_time_window(timestamp)
        if result is not None:
            return Response(result)

        result = NewsletterEmailProcessor.process_get_new_newsletter_emails(request, is_all)
        return Response(result)


urlpatterns = [
    url(r'^emails$', EmailsView.as_view()),
    ]