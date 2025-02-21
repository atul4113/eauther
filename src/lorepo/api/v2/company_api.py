from django.conf.urls import url
from django.core.validators import URLValidator
from django.utils.decorators import method_decorator
from lorepo.corporate.models import CompanyProperties
from lorepo.permission.decorators import has_space_access
from lorepo.permission.models import Permission
from lorepo.permission.util import get_company_for_user
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import views
from google.appengine.api import urlfetch


class CompanyView(views.APIView):
    permission_classes = (IsAuthenticated, )

    """
    @api {put} /api/v2/company/ /
    @apiDescription putting callback url to companyproperties
    @apiName Company
    @apiGroup Company
    @apiPermission Permission.CONTENT_VIEW
    @apiParam {String} [callback_url]
    @apiParamExample {json} Request-Example:
                 { "callback_url": "http://example.com/export_confirm" }
    @apiHeader {String} Authorization User Token.
    @apiHeaderExample {json} Header-Example:
      {
        "Authorization": "JWT TOKEN"
      }

    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK

    """

    @method_decorator(has_space_access(Permission.CONTENT_VIEW))
    def put(self, *args, **kwargs):
        callback_url = self.request.data.get('callback_url', None)
        if callback_url is None:
            raise ValidationError('No callback_url provided.')

        validate = URLValidator()
        try:
            validate(callback_url)
        except:
            raise ValidationError('Callback Url is not valid.')

        response = urlfetch.fetch(url=callback_url, method=urlfetch.GET, deadline=10)
        if response.status_code != 200:
            raise ValidationError('Callback_url not responding')

        company = get_company_for_user(self.request.user)

        companyproperties = CompanyProperties.objects.get(company=company)
        companyproperties.callback_url = callback_url
        companyproperties.save()

        return Response({})



urlpatterns = [
    url(r'^$', CompanyView.as_view(), name='company_properties'),
    ]