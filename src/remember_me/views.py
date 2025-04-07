from django.contrib.auth import REDIRECT_FIELD_NAME, login, authenticate
from django.views.decorators.cache import never_cache
from django.utils.http import url_has_allowed_host_and_scheme
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.conf import settings
from django.contrib.auth.models import User
from src.lorepo.spaces.models import SpaceAccess
from src.remember_me.forms import AuthenticationRememberMeForm

@never_cache
def remember_me_login(request, redirect_field_name=REDIRECT_FIELD_NAME):
    """
    Displays the login form with a remember me checkbox and handles login.
    """
    redirect_to = request.POST.get(redirect_field_name, '')

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect("/")  # or redirect wherever you want
        else:
            print("Authentication failed")
        form = AuthenticationRememberMeForm(data=request.POST)

        if form.is_valid():
            # user = request.POST.get("user")
            user = form.get_user()

            # Validate redirect URL
            if not url_has_allowed_host_and_scheme(redirect_to, allowed_hosts={request.get_host()}):
                redirect_to = settings.LOGIN_REDIRECT_URL

            # Handle session expiry based on 'remember me' option
            if not form.cleaned_data.get('remember_me', False):
                request.session.set_expiry(0)

            login(request, user)

            # Fetch spaces
            # spaces = SpaceAccess.objects.filter(user=user).exclude(space__title=user.username)
            # First, get all spaces where the user has access
            spaces = SpaceAccess.objects.filter(user=user)

            # Then, filter manually in Python (since exclude() causes issues)
            spaces = [s for s in spaces if s.space.title != user.username]

            if len(spaces) > 0 and redirect_to != '/corporate/create_trial_account':
                redirect_to = '/corporate/no_space_info'

            return HttpResponseRedirect(redirect_to)

        # If form is invalid, render login page with errors
        return render(request, '../templates/login.html', {'form': form})

    # Show login form on GET request
    return render(request, '../templates/login.html', {'form': AuthenticationRememberMeForm()})
