from lorepo.user.models import UserLanguage
from registration.forms import RegistrationFormTermsOfService
from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.template import loader
from django.utils.http import urlsafe_base64_encode
from django.template.context import Context
from settings import USER_LANGUAGES

attrs_dict = { 'class': 'required' }

class CustomRegistrationForm(RegistrationFormTermsOfService):

    url = '<a href="/user/terms">Terms of use</a>'
    tos = forms.BooleanField(widget=forms.CheckboxInput(attrs=attrs_dict),
                             label=mark_safe(_('I have read and agree to the ' + url)),
                             error_messages={ 'required': "You must agree to the terms to register" })
    email2 = forms.EmailField(widget=forms.TextInput(attrs=dict(attrs_dict,
                                                               maxlength=75)),
                             label=_('email address (again)'))
    def clean(self):
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
                if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                    raise forms.ValidationError(_('You must type the same password each time'))
        if 'email' in self.cleaned_data and 'email2' in self.cleaned_data:
                if self.cleaned_data['email'] != self.cleaned_data['email2']:
                    raise forms.ValidationError(_('You must type the same email address each time'))
        return self.cleaned_data
    
class EmailChangeForm(forms.Form):
    email = forms.EmailField(label=_("E-mail"), max_length=75)
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(EmailChangeForm, self).__init__(*args, **kwargs)
        
    def save(self, commit=True):
        self.user.email = self.cleaned_data['email']
        if commit:
            self.user.save()
        return self.user

class LanguageChoiceForm(forms.Form):
    language = forms.ChoiceField(choices=USER_LANGUAGES, )

    def __init__(self,user, *args, **kwargs):
        self.user = user
        language = user.profile.language_code
        super(LanguageChoiceForm, self).__init__(initial={'language':language}, *args, **kwargs)

    def save(self, commit=True):
        user_profile = self.user.profile
        user_profile.language_code = self.cleaned_data['language']
        if commit:
            user_profile.save()

class CustomPasswordResetForm(forms.Form):
    username = forms.CharField(max_length=75)

    def clean_username(self):
        """
        Validates that an active user exists with the given username.
        """
        username = self.cleaned_data["username"]
        self.users_cache = User.objects.filter(
                                username = username,
                                is_active = True
                            )
        if len(self.users_cache) == 0:
            raise forms.ValidationError(("That username doesn't exist. Are you sure you've registered?"))
        return username

    def save(self, domain_override=None, email_template_name='registration/password_reset_email.html',
             subject_template_name='registration/password_reset_subject.txt',
             html_email_template_name=None,
             use_https=False, token_generator=default_token_generator, from_email=None, request=None):
        """
        Generates a one-use only link for resetting password and sends to the user
        """
        from django.core.mail import send_mail
        for user in self.users_cache:
            if not domain_override:
                current_site = get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain
            else:
                site_name = domain = domain_override
            t = loader.get_template(email_template_name)
            c = {
                'email': user.email,
                'domain': domain,
                'site_name': site_name,
                'uid': urlsafe_base64_encode(str(user.id)),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': use_https and 'https' or 'http',
            }
            send_mail(("Password reset on %s") % site_name,
                t.render(Context(c)), from_email, [user.email])