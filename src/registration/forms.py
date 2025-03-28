from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User

from src.registration.models import RegistrationProfile

attrs_dict = {'class': 'required'}


class RegistrationForm(forms.Form):
    """
    Datastore-compatible registration form that avoids transaction issues
    """
    username = forms.RegexField(
        regex=r'^\w+$',
        max_length=30,
        widget=forms.TextInput(attrs=attrs_dict),
        label=_('username')
    )
    email = forms.EmailField(
        widget=forms.TextInput(attrs=dict(attrs_dict, maxlength=75)),
        label=_('email address')
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
        label=_('password')
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
        label=_('password (again)')
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'registrationInput'

    def clean_username(self):
        username = self.cleaned_data['username']

        # First check exact match (uses index)
        if User.objects.filter(username=username).first():
            raise forms.ValidationError("This username is already taken.")

        # Then check case variations (slower but works without transactions)
        if any(u.username.lower() == username.lower()
               for u in User.objects.only('username').iterator()):
            raise forms.ValidationError("Username exists with different case.")

        return username

    def clean_email(self):
        email = self.cleaned_data['email']

        # First check exact match
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")

        # Then check case variations
        if any(u.email.lower() == email.lower()
               for u in User.objects.only('email').iterator()):
            raise forms.ValidationError("Email exists with different case.")

        return email

    def clean(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match.")
        return self.cleaned_data

    def save(self, profile_callback=None):
        """
        Create user without wrapping in transaction to avoid Datastore errors
        """
        # Get the create_inactive_user method directly
        create_user = RegistrationProfile.objects.create_inactive_user

        # Call it without any transaction
        return create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password1'],
            email=self.cleaned_data['email'],
            profile_callback=profile_callback
        )