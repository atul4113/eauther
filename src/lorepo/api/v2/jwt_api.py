from django.http import HttpResponseBadRequest
from rest_framework.request import Request
from rest_framework import generics
from rest_framework_jwt.settings import api_settings
from django.conf.urls import patterns, url, include
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
jwt_response_payload_handler = api_settings.JWT_RESPONSE_PAYLOAD_HANDLER


"""
@api {POST} /api/v2/jwt/obtain-token/ /jwt/obtain-token/
@apiName Obtain token
@apiDescription API View that receives a POST with a user's username and password.
                Returns a JSON Web Token that can be used for authenticated requests.
@apiGroup Token
@apiParam {String} username (required) - username
@apiParam {String} password (required) - password

@apiSuccessExample {json} Success-Response:
  HTTP/1.1 200 OK
    {
      token: "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjo2MDU0OTc2MTc0NDI0MDY0LCJlbWFpbCI6Im1pY2hhbC56YXJ6eWNraUBzb2x3aXQuY29tIiwidXNlcm5hbWUiOiJhIiwib3JpZ19pYXQiOjE0NjkwMjg5MjUsImV4cCI6MTQ2OTAzMTkyNX0.rid7lFBVSEME7AQxaHM55M61G2V-lyJ69JgIsv5SJg0"
    }

@apiErrorExample {json} Error-Response:
  HTTP/1.1 400 Bad Request
    {
      non_field_errors: [
        "Unable to login with provided credentials."
      ]
    }
"""
urlpatterns = patterns('rest_framework_jwt.views',
    url(r'^obtain-token/', 'obtain_jwt_token'),
)


"""
@api {get} /api/v2/jwt/refresh_jwt_token/ /jwt/refresh_jwt_token/
@apiName Refresh token
@apiDescription API View that returns a refreshed token (with new expiration) based on
                existing token
                If 'orig_iat' field (original issued-at-time) is found, will first check
                if it's within expiration window, then copy it to the new token
@apiGroup Token
@apiParam {String} token (required) - token what status is expired

@apiSuccessExample {json} Success-Response:
  HTTP/1.1 200 OK
    {
      token: "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjo2MDU0OTc2MTc0NDI0MDY0LCJlbWFpbCI6Im1pY2hhbC56YXJ6eWNraUBzb2x3aXQuY29tIiwidXNlcm5hbWUiOiJhIiwib3JpZ19pYXQiOjE0NjkwMjg5MjUsImV4cCI6MTQ2OTAzMTkyNX0.rid7lFBVSEME7AQxaHM55M61G2V-lyJ69JgIsv5SJg0"
    }

@apiErrorExample {json} Error-Response:
  HTTP/1.1 400 Bad Request
    {
      non_field_errors: [
        "Unable to login with provided credentials."
      ]
    }
"""




urlpatterns += patterns('rest_framework_jwt.views',
        url(r'^refresh-token/', 'refresh_jwt_token'),
)


class SessionToken(generics.GenericAPIView):
    """
    @api {get} /api/v2/jwt/session_token /jwt/session_token
    @apiName Session token
    @apiDescription get session token
    @apiGroup Token
    @apiParam {String} token (required) - token what status is expired

    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK
        {
          token: "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjo2MDU0OTc2MTc0NDI0MDY0LCJlbWFpbCI6Im1pY2hhbC56YXJ6eWNraUBzb2x3aXQuY29tIiwidXNlcm5hbWUiOiJhIiwib3JpZ19pYXQiOjE0NjkwMjg5MjUsImV4cCI6MTQ2OTAzMTkyNX0.rid7lFBVSEME7AQxaHM55M61G2V-lyJ69JgIsv5SJg0"
        }

    @apiErrorExample {json} Error-Response:
      HTTP/1.1 400 Bad Request
        {
          non_field_errors: [
            "Unable to login with provided credentials."
          ]
        }
    """
    authentication_classes = (SessionAuthentication,)
    box_type = None

    def get(self, request):
        if not request.user.is_authenticated():
            return HttpResponseBadRequest('{"non_field_errors":["Unable to login with provided credentials."]}',
                                          content_type='application/json')
        payload = jwt_payload_handler(request.user)
        token = jwt_encode_handler(payload)
        response_data = jwt_response_payload_handler(token, request.user, Request(request))
        return Response(response_data)


urlpatterns += [
        url(r'^session_token$', SessionToken.as_view(), name='session_token')
    ]



