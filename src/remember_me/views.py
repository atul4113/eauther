from django.contrib.auth import REDIRECT_FIELD_NAME, login, authenticate
from django.views.decorators.cache import never_cache
from django.utils.http import url_has_allowed_host_and_scheme
from django.shortcuts import render, redirect
from django.conf import settings
from src.lorepo.spaces.models import SpaceAccess
from src.remember_me.forms import AuthenticationRememberMeForm

@never_cache
def remember_me_login(request, redirect_field_name=REDIRECT_FIELD_NAME):
    redirect_to = request.POST.get(redirect_field_name, settings.LOGIN_REDIRECT_URL)

    if request.method == "POST":
        form = AuthenticationRememberMeForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()

            # Validate redirect URL
            if not url_has_allowed_host_and_scheme(redirect_to, allowed_hosts={request.get_host()}):
                redirect_to = settings.LOGIN_REDIRECT_URL

            # Handle session expiry based on 'remember me' checkbox
            if not form.cleaned_data.get('remember_me'):
                request.session.set_expiry(0)  # Expires on browser close
            else:
                request.session.set_expiry(settings.SESSION_COOKIE_AGE)  # Default expiry

            login(request, user)

            # Fetch spaces
            spaces = SpaceAccess.objects.filter(user=user)
            spaces = [s for s in spaces if s.space.title != user.username]

            if len(spaces) > 0 and redirect_to != '/corporate/create_trial_account':
                redirect_to = '/corporate/no_space_info'

            return redirect(redirect_to)

        # Form is invalid
        return render(request, '../templates/login.html', {'form': form})

    # GET request: show the login form
    form = AuthenticationRememberMeForm()
    return render(request, '../templates/login.html', {'form': form})
