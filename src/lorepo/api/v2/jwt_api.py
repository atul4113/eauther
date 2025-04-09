from django.http import HttpResponseBadRequest
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.urls import path, re_path

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
jwt_response_payload_handler = api_settings.JWT_RESPONSE_PAYLOAD_HANDLER


class SessionToken(generics.GenericAPIView):
    """
    API endpoint that returns a JWT token for users with active sessions.
    """
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Generate a JWT token for an already authenticated session user.
        """
        try:
            payload = jwt_payload_handler(request.user)
            token = jwt_encode_handler(payload)
            response_data = jwt_response_payload_handler(token, request.user, request)
            return Response(response_data)
        except Exception as e:
            return HttpResponseBadRequest(
                '{"non_field_errors":["Unable to generate token for session."]}',
                content_type='application/json'
            )


# Single consolidated urlpatterns definition
urlpatterns = [
    # JWT Token endpoints
    path('obtain-token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh-token/', TokenRefreshView.as_view(), name='token_refresh'),
    path('session-token/', SessionToken.as_view(), name='session_token'),

    # Legacy JWT endpoint (if needed)
    re_path(r'^session[-_]{1}token/?$', SessionToken.as_view(), name='session_token'),]
