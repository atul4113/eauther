import requests
from django.urls import path
from django.core.validators import URLValidator
from django.utils.decorators import method_decorator
from src.lorepo.corporate.models import CompanyProperties
from src.lorepo.permission.decorators import has_space_access
from src.lorepo.permission.models import Permission
from src.lorepo.permission.util import get_company_for_user
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular import views


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

        try:
            response = requests.get(callback_url, timeout=10)
        except requests.exceptions.RequestException as e:
            raise ValidationError(f'Error while contacting callback URL: {str(e)}')

        if response.status_code != 200:
            raise ValidationError('Callback URL is not responding.')

        company = get_company_for_user(self.request.user)

        companyproperties = CompanyProperties.objects.get(company=company)
        companyproperties.callback_url = callback_url
        companyproperties.save()

        return Response({})



urlpatterns = [
    path('', CompanyView.as_view(), name='company_properties'),
    ]