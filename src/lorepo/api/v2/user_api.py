from django.urls import path
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import get_object_or_404
from django.template import loader
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from src import settings
from src.lorepo.api.v2.mixins import MiddlewareMixin
from src.lorepo.corporate.middleware import CorporateMiddleware
from src.lorepo.corporate.models import CorporateLogo
from src.lorepo.corporate.templatetags.corporate import is_any_division_admin
from src.lorepo.permission.models import Role
from src.lorepo.public.util import send_message
from src.lorepo.spaces.serializers import SpaceSerializer, PermissionRoleSerializer
from src.lorepo.spaces.util import get_private_space_for_user
from src.lorepo.user.serializers import PasswordFormSerializer, ProfileChangeFormSerializer
from rest_framework import views, generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular import serializers as s


class UserData(MiddlewareMixin, views.APIView):
    """
    @api {get} /api/v2/user/ /user/
    @apiDescription Roles and basic information about user
    @apiName UserData
    @apiGroup User

    @apiHeader {String} Authorization User Token.
    @apiHeaderExample {json} Header-Example:
      {
        "Authorization": "JWT TOKEN"
      }

    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK
      {
          id: 6077825400438784,
          email: "michal.zarzycki@solwit.com",
          username: "g",
          language_code: "en",
          is_superuser: true
      }
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            profile = request.user.profile
            language_code = profile.language_code if hasattr(profile, 'language_code') else 'en'
        except AttributeError:
            language_code = 'en'  # Default value if profile doesn't exist

        context = {'request': request}
        private_space = get_private_space_for_user(request.user)

        response_data = {
            'id': request.user.id,
            'username': request.user.username,
            'email': request.user.email,
            'is_superuser': request.user.is_superuser,
            'language_code': language_code,
            'company': None,
            'public_category': None,
            'private_space': None,
            'is_any_division_admin': is_any_division_admin(request.user)
        }

        # Only try to serialize if the relationships exist
        if hasattr(request.user, 'company') and request.user.company:
            response_data['company'] = SpaceSerializer(request.user.company, context=context).data

        if hasattr(request.user, 'public_category') and request.user.public_category:
            response_data['public_category'] = SpaceSerializer(request.user.public_category, context=context).data

        if private_space:
            response_data['private_space'] = SpaceSerializer(private_space, context=context).data

        return Response(response_data)


class RemindLogin(generics.GenericAPIView):
    """
    @api {post} /api/v2/remind_login /remind_login
    @apiDescription Reminds login
    @apiName RemindLogin
    @apiGroup User

    @apiParam {String} email (required) - email

    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK
      {
        'reminded': true
      }
    @apiErrorExample {json} Error-Response:
      HTTP/1.1 400 Bad Request
      ["E-mail does not exist."]
    """

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        if not email:
            raise ValidationError('Email is required.')

        logins = User.objects.filter(email=email)
        if not logins.exists():
            raise ValidationError('E-mail does not exist.')

        c = {
            'logins': logins,
            'email': email,
            'request': request
        }
        email_template_name = 'src/registration/remind_login_email.html'
        t = loader.get_template(email_template_name)
        from_email = settings.SERVER_EMAIL

        send_message(from_email, [email],
                     'remind_login.email_subject',
                     t.render(c))
        return Response({'reminded': True})


class ResetPassword(generics.GenericAPIView):
    """
    @api {get} /api/v2/user/reset_password /user/reset_password
    @apiDescription Request to send email with reset link
    @apiName RequestToSendResetEmail
    @apiGroup User

    @apiParam {String} username (required) - username

    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK

    @apiErrorExample {json} Error-Response:
      HTTP/1.1 404 Not Found
    """

    def get(self, request, username, *args, **kwargs):
        user = get_object_or_404(User, username=username, is_active=True)
        token = default_token_generator.make_token(user)

        from_email = settings.SERVER_EMAIL
        email_template_name = 'src/registration/password_reset_email.html'
        current_site = get_current_site(request)
        site_name = current_site.name
        domain = current_site.domain
        use_https = request.is_secure()

        t = loader.get_template(email_template_name)
        c = {
            'email': user.email,
            'domain': domain,
            'site_name': site_name,
            'uid': urlsafe_base64_encode(force_bytes(str(user.id))),
            'user': user,
            'token': token,
            'protocol': use_https and 'https' or 'http',
            'request': request
        }
        send_message(from_email, [user.email],
                     'src.lorepo.user.reset_password.Password_reset_on_',
                     t.render(c))

        return Response('ok')

    def post(self, request, *args, **kwargs):
        token = request.data.get('token')
        if not token:
            raise ValidationError('Token is required')

        try:
            uid, pass_token = self._split_token(token)
            user = self._get_user(uid)
        except (ValueError, User.DoesNotExist):
            raise ValidationError('token is invalid')

        if not default_token_generator.check_token(user, pass_token):
            raise ValidationError('token is invalid')

        return Response('ok')

    def put(self, request, *args, **kwargs):
        token = request.data.get('token')
        password1 = request.data.get('password1')
        password2 = request.data.get('password2')

        if not token or not password1 or not password2:
            raise ValidationError('All fields are required')

        if password1 != password2:
            raise ValidationError('password does not match')

        try:
            uid, pass_token = self._split_token(token)
            user = self._get_user(uid)
        except (ValueError, User.DoesNotExist):
            raise ValidationError('token is invalid')

        if not default_token_generator.check_token(user, pass_token):
            raise ValidationError('token is invalid')

        user.set_password(password1)
        user.save()
        return Response('ok')

    def _split_token(self, token):
        uidb64, pass_token = token.split('-', 1)
        uid = force_str(urlsafe_base64_decode(uidb64))
        return uid, pass_token

    def _get_user(self, user_id):
        return get_object_or_404(User, pk=user_id)


class EditUser(generics.GenericAPIView):
    """
    @api {post} /api/v2/user/edit /user/edit
    @apiDescription change data in user profile
    @apiName EditUser
    @apiGroup User

    @apiHeader {String} Authorization User Token.
    @apiHeaderExample {json} Header-Example:
      {
        "Authorization": "JWT TOKEN"
      }

    @apiParam {String} email (required) - user email

    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK
      {
        "status": "OK"
      }
    @apiErrorExample {json} Error-Response:
      HTTP/1.1 400 Bad Request
      {
        {"email":["'This field may not be blank."]}
      }
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = ProfileChangeFormSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status': 'OK'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserPassword(generics.GenericAPIView):
    """
    @api {post} /api/v2/user/password /user/password
    @apiDescription Change user password, required old password
    @apiName Password
    @apiGroup User

    @apiHeader {String} Authorization User Token.
    @apiHeaderExample {json} Header-Example:
      {
        "Authorization": "JWT TOKEN"
      }

    @apiParam {String} old_password (required) - user old password
    @apiParam {new_password1} new_password1 - user new password1
    @apiParam {new_password2} new_password2 - user new password2

    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK
      {
        "status": "OK"
      }
    @apiErrorExample {json} Error-Response:
      HTTP/1.1 400 Bad Request
      {
        {"old_password":{"code":"0","message":"Old password is incorrect."}}
      }
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = PasswordFormSerializer

    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        data['user'] = request.user

        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status': 'OK'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLogo(MiddlewareMixin, views.APIView):
    """
    @api {get} /api/v2/user/logo/ /user/logo/
    @apiDescription Company user logo
    @apiName UserData
    @apiGroup User

    @apiHeader {String} Authorization User Token.
    @apiHeaderExample {json} Header-Example:
      {
        "Authorization": "JWT TOKEN"
      }

    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK
      {
          logo: 6077825400438784,
      }
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        if not hasattr(request.user, 'company'):
            return Response(None)

        corporate_logo = CorporateLogo.objects.filter(space=request.user.company).first()
        return Response(corporate_logo.logo.id if corporate_logo and corporate_logo.logo else None)


urlpatterns = [
    path('', UserData.as_view(), name='user_data'),
    path('edit/', EditUser.as_view(), name='edit_user'),
    path('password/', UserPassword.as_view(), name='user_password'),
    path('remind_login/', RemindLogin.as_view(), name='remind_login'),
    path('reset_password/', ResetPassword.as_view(), name='reset_password'),
    path('reset_password/<str:username>/', ResetPassword.as_view(), name='reset_password_with_username'),
    path('logo/', UserLogo.as_view(), name='logo'),
]