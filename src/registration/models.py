import random
import re
import hashlib
import datetime

from django.conf import settings
from django.db import models
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.utils import timezone

SHA1_RE = re.compile(r'^[a-f0-9]{40}$')
User = get_user_model()


class RegistrationManager(models.Manager):
    def activate_user(self, activation_key):
        if SHA1_RE.fullmatch(activation_key):
            try:
                profile = self.get(activation_key=activation_key)
            except self.model.DoesNotExist:
                return False
            if not profile.activation_key_expired():
                user = profile.user
                user.is_active = True
                user.save()
                profile.activation_key = self.model.ACTIVATED
                profile.save()
                return user
        return False

    def create_inactive_user(self, username, password, email, send_email=True, profile_callback=None):
        new_user = User.objects.create_user(username=username, email=email, password=password)
        new_user.is_active = False
        new_user.save()

        registration_profile = self.create_profile(new_user)

        if profile_callback:
            profile_callback(user=new_user)

        if send_email:
            from django.core.mail import send_mail
            subject = render_to_string('registration/activation_email_subject.txt', {}).strip()
            message = render_to_string('registration/activation_email.txt', {
                'activation_key': registration_profile.activation_key,
                'expiration_days': getattr(settings, 'ACCOUNT_ACTIVATION_DAYS', 7),
                'settings': settings
            })
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [new_user.email])
        return new_user

    def create_profile(self, user):
        salt = hashlib.sha256(str(random.random()).encode()).hexdigest()[:5]
        activation_key = hashlib.sha256((salt + user.username).encode()).hexdigest()
        return self.create(user=user, activation_key=activation_key)

    def delete_expired_users(self):
        expiration_days = getattr(settings, 'ACCOUNT_ACTIVATION_DAYS', 7)
        expiration_date = timezone.now() - datetime.timedelta(days=expiration_days)
        expired_profiles = self.filter(user__date_joined__lte=expiration_date, user__is_active=False)
        expired_profiles.delete()


class RegistrationProfile(models.Model):
    ACTIVATED = "ALREADY_ACTIVATED"

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=_('user'))
    activation_key = models.CharField(_('activation key'), max_length=64)

    objects = RegistrationManager()

    class Meta:
        verbose_name = _('registration profile')
        verbose_name_plural = _('registration profiles')

    def __str__(self):
        return f"Registration information for {self.user}"

    def activation_key_expired(self):
        expiration_days = getattr(settings, 'ACCOUNT_ACTIVATION_DAYS', 7)
        expiration_date = self.user.date_joined + datetime.timedelta(days=expiration_days)
        return self.activation_key == self.ACTIVATED or expiration_date <= timezone.now()

    activation_key_expired.boolean = True