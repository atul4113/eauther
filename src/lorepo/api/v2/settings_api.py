from collections import OrderedDict

from django.conf.urls import url
from google.appengine.api.app_identity import get_application_id

import settings
from libraries.utility.environment import get_app_version
from lorepo.global_settings.models import GlobalSettings
from lorepo.translations.models import SupportedLanguages
from rest_framework import views
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
    def get(self, request):

        response_data = OrderedDict((
            ('lang', settings.USER_DEFAULT_LANG),
            ('email', settings.SERVER_EMAIL),
            ('select_user_language', False),
        ))

        response_data['version'] = get_app_version()
        response_data['application_id'] = get_application_id()
        response_data['supported_languages'] = SupportedLanguages.get_languages_json()
        response_data['referrers'] = GlobalSettings.get_cached().referrers

        return Response(response_data)

urlpatterns = [
    url(r'^$', SettingsView.as_view(), name='settings'),
]
