from .urls import path
from django.contrib.auth.models import User
from src.registration.models import RegistrationProfile
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import get_object_or_404
from django.template import loader, Context
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
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
from rest_framework.fields import EmailField
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular import serializers as s


class UserData(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        print("\n=== UserData View Called ===")
        print("User:", request.user)
        print("Auth Header:", request.headers.get('Authorization'))

        try:
            context = {'request': request}
            profile = request.user.profile
            private_space = get_private_space_for_user(request.user)

            return Response({
                'id': request.user.id,
                'username': request.user.username,
                'email': request.user.email,
                'is_superuser': request.user.is_superuser,
                'language_code': profile.language_code if hasattr(profile, 'language_code') else 'en',
                'company': None if not hasattr(request.user, 'company') or request.user.company is None
                else SpaceSerializer(request.user.company, context=context).data,
                'public_category': None if not hasattr(request.user,
                                                       'public_category') or request.user.public_category is None
                else SpaceSerializer(request.user.public_category, context=context).data,
                'private_space': None if private_space is None
                else SpaceSerializer(private_space, context=context).data,
                'is_any_division_admin': is_any_division_admin(request.user)
            })

        except Exception as e:
            print("Error in UserData:", str(e))
            return Response({'error': str(e)}, status=400)

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
        data = request.data.copy()
        email = data['email']
        logins = User.objects.filter(email=email)

        if logins:
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
                         t.render(Context(c)))
            return Response({'reminded': True})
        else:
            raise ValidationError('E-mail does not exist.')


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

    """
    @api {post} /api/v2/user/reset_password /user/reset_password
    @apiDescription Check if provided token is valid
    @apiName CheckToken
    @apiGroup User

    @apiParam {String} token (required) - token

    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK

    @apiErrorExample {json} Error-Response:
      HTTP/1.1 400 Bad Request
      ["token is invalid"]
    """

    """
    @api {put} /api/v2/user/reset_password /user/reset_password
    @apiDescription Reset password
    @apiName ResetPassword
    @apiGroup User

    @apiParam {String} token (required) - token
    @apiParam {String} password1 (required) - password1
    @apiParam {String} password2 (required) - password2

    @apiSuccessExample {json} Success-Response:
      HTTP/1.1 200 OK

    @apiErrorExample {json} Error-Response:
      HTTP/1.1 400 Bad Request
      ["password does not match"]
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
            'uid': urlsafe_base64_encode(str(user.id)),
            'user': user,
            'token': token,
            'protocol': use_https and 'https' or 'http',
            'request': request
        }
        send_message(from_email, [user.email],
                     'src.lorepo.user.reset_password.Password_reset_on_',
                     t.render(Context(c)))

        return Response('ok')

    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        token = data['token']
        uid, pass_token = self._split_token(token)
        user = self._get_user(uid)

        if default_token_generator.check_token(user, pass_token):
            return Response('ok')
        raise ValidationError('token is invalid')

    def put(self, request, *args, **kwargs):
        data = request.data.copy()
        token = data['token']
        uid, pass_token = self._split_token(token)

        password1 = data['password1']
        password2 = data['password2']

        if password1 != password2:
            raise ValidationError('password does not match')

        user = self._get_user(uid)

        if not default_token_generator.check_token(user, pass_token):
            raise ValidationError('token is invalid')

        # do reset
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
        data = request.data.copy()
        data['user'] = request.user

        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            response = serializer.save()
            st = status.HTTP_200_OK
        else:
            response = serializer.errors
            st = status.HTTP_400_BAD_REQUEST
        return Response(response, status=st)





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
            response = serializer.save()
            st = status.HTTP_200_OK
        else:
            response = serializer.errors
            st = status.HTTP_400_BAD_REQUEST
        return Response(response, status=st)


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
    permission_classes = (IsAuthenticated, )
    MIDDLEWARE_CLASSES = (CorporateMiddleware, )

    def get(self, request):
        logo = None
        corporate_logo_list = CorporateLogo.objects.filter(space=request.user.company)
        if len(corporate_logo_list) > 0:
            logo = corporate_logo_list[0].logo

        return Response(logo.id if logo else None)


urlpatterns = [
    path('', UserData.as_view(), name='user_data'),
    path('edit/', EditUser.as_view(), name='edit_user'),
    path('password/', UserPassword.as_view(), name='user_password'),
    path('remind_login/', RemindLogin.as_view(), name='remind_login'),
    path('reset_password/', ResetPassword.as_view(), name='reset_password'),
    path('reset_password/<str:username>/', ResetPassword.as_view(), name='reset_password'),
    path('logo/', UserLogo.as_view(), name='logo'),
]