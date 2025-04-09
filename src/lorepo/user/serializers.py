from django.contrib.auth.models import User
import src.libraries.utility.cacheproxy as cache
from src.lorepo.permission.models import Role, Permission
from src.lorepo.spaces.models import Space, SpaceAccess
from src.lorepo.spaces.service import insert_space
from src.lorepo.user.models import UserProfile
from src.registration.models import RegistrationProfile
from rest_framework import serializers as s
from rest_framework.exceptions import ValidationError
from rest_framework.fields import RegexField, EmailField


class RegistrationSerializer(s.Serializer):
    username = RegexField(regex=r'^[a-zA-Z0-9_]+$', max_length=30, min_length=1, required=True)
    password1 = s.CharField(required=True)
    password2 = s.CharField(required=True)
    email = s.EmailField()
    email_confirmed = s.EmailField()
    regulation_agreement = s.BooleanField(required=True)


    def profile_callback(self, user):
        data = {'user': user}
        profile = UserProfile(**data)
        profile.save()

        #initiate spaces
        space = Space(title=user.username)
        insert_space(space)
        role = Role(name='owner', permissions=Permission().get_all())
        role.save()
        space_access = SpaceAccess(user=user, space=space, roles=[role.pk])
        space_access.save()
        return profile

    def validate_username(self, value):
        try:
            user = User.objects.get(username=value.lower())
        except User.DoesNotExist:
            return value

        raise s.ValidationError({'message': 'Username already taken', 'code': 0})

    def validate_regulation_agreement(self, value):
        if value:
            return value
        raise s.ValidationError({'message': 'Regulation aggrement required', 'code': 3})

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise ValidationError({'message': 'Not the same passwords', 'code': 1})
        if data['email'] != data['email_confirmed']:
            raise ValidationError({'message': 'Not the same emails', 'code': 2})
        return data

    def save(self):
        cache_key = 'register_username_%s' % self.validated_data['username'] #race condition
        if cache.get(cache_key) is not None:
            raise s.ValidationError({'message': 'Username already taken', 'code': 0})
        cache.set(cache_key, self.validated_data['username'], 5)

        new_user = RegistrationProfile.objects.create_inactive_user(username=self.validated_data['username'],
                                                                password=self.validated_data['password1'],
                                                                email=self.validated_data['email'],
                                                                profile_callback=self.profile_callback)

        return new_user


class PasswordFormSerializer(s.Serializer):
    old_password = s.CharField()
    new_password1 = s.CharField()
    new_password2 = s.CharField()

    def validate_old_password(self, old_password):
        """
        Validates that the old_password field is correct.
        """
        user = self.initial_data['user']

        if not user.check_password(old_password):
            raise s.ValidationError({'message': 'Old password is incorrect.', 'code': 0})
        return old_password

    def validate(self, data):
        if data['new_password1'] != data['new_password2']:
            raise s.ValidationError({'message': 'You must type the same password each time', 'code': 1})
        return data

    def save(self):
        user = self.initial_data['user']
        user.set_password(self.validated_data['new_password1'])
        user.save()
        return {
            'status': 'OK'
        }


class ProfileChangeFormSerializer(s.Serializer):

    email = EmailField(max_length=75, required=False)


    def save(self):
        user = self.initial_data['user']

        if self.validated_data.get('email'):  # we do allow empty email address in form but change only should be done if it's filled
            user.email = self.validated_data['email']


        if self.validated_data.get('email'):
            user.save()

        return {
            'status': 'OK'
        }
