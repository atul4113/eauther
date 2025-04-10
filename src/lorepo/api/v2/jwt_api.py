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
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.urls import path, re_path

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
jwt_response_payload_handler = api_settings.JWT_RESPONSE_PAYLOAD_HANDLER

class SessionToken(APIView):
    """
    API endpoint that returns a JWT token for users with active sessions.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Generate a JWT token for an already authenticated session user.
        """
        from rest_framework_simplejwt.tokens import RefreshToken

        refresh = RefreshToken.for_user(request.user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })

# Single consolidated urlpatterns definition
urlpatterns = [
    # JWT Token endpoints
    path('obtain-token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh-token/', TokenRefreshView.as_view(), name='token_refresh'),
    path('session-token/', SessionToken.as_view(), name='session_token'),

    # Legacy JWT endpoint (if needed)
    re_path(r'^session[-_]{1}token/?$', SessionToken.as_view(), name='session_token'),]
