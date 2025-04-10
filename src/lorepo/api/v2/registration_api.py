from rest_framework.permissions import AllowAny

from src.lorepo.user.serializers import RegistrationSerializer
from src.registration.models import RegistrationProfile
from rest_framework import status, generics
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response


class RegisterUser(generics.GenericAPIView):
    permission_classes = [AllowAny]  # Allow any user to access this endpoint

    serializer_class = RegistrationSerializer

    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        serializer = self.get_serializer(data=data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_serializer_context(self):
        return {
            'user_lang_key': self.request.COOKIES.get('USER_LANG'),
            'request': self.request
        }


class RegisterUserActivate(generics.GenericAPIView):
    """
    @api {post} /api/v2/register/activate /register/activate
    @apiDescription Activate registered account
    @apiName RegisterUserActivate
    @apiGroup User

    @apiParam {String} activation_key (required) - activation key

    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK
      {
        'activated': true
      }
    @apiErrorExample {json} Error-Response:
      HTTP/1.1 400 Bad Request
      ["Key has expired or does not exist."]
    """

    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        key = data['activation_key']

        activation_key = key.lower()  # Normalize before trying anything with it.
        account, _ = RegistrationProfile.objects.activate_user(activation_key)

        if account:
            return Response({'activated': True})
        raise ValidationError('Key has expired or does not exist.')
