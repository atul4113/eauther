from collections import OrderedDict
from django.urls import path
from rest_framework.permissions import AllowAny

from src import settings
from src.libraries.utility.environment import get_app_version
from src.lorepo.global_settings.models import GlobalSettings
from src.lorepo.translations.models import SupportedLanguages
from drf_spectacular import views
from rest_framework.response import Response

class SettingsView(views.APIView):
    """
    @api {get} /api/v2/settings /settings
    @apiDescription Global Settings Endpoint
    @apiName AppSettings
    @apiGroup Application Settings

    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK
      {
      email: "mcourser.com <admin@muathor.com>",
      lang: "en_US",
      version: "356",
      application_name: "lorepocorporate",
      select_user_language: false,
      supported_languages: [
            {
                "description": "english do usuniecia",
                "id": 4987281664376832,
                "key": "en_US6"
            },
            {
                "description": "english do usuniecia",
                "id": 5724160613416960,
                "key": "en_US7"
            }
        ]
    }
    """
    permission_classes = [AllowAny]  # Add this line to allow public access
    def get(self, request):
        # Prepare the response data
        response_data = OrderedDict((
            ('lang', settings.USER_DEFAULT_LANG),
            ('email', settings.SERVER_EMAIL),
            ('select_user_language', False),
        ))

        response_data['version'] = get_app_version()
        # Removed get_application_id() as it is specific to App Engine
        # You can include a fallback or custom application ID if needed
        response_data['application_name'] = settings.APP_NAME  # or another way to get the app name
        response_data['supported_languages'] = SupportedLanguages.get_languages_json()
        response_data['referrers'] = GlobalSettings.get_cached().referrers

        return Response(response_data)

urlpatterns = [
    path('', SettingsView.as_view(), name='settings'),
]
