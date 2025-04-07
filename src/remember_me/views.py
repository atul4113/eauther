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
        print(request.POST, "request.POST........................////////////////////////")
        username = request.POST.get("username")
        password = request.POST.get("password")
        print("username = ",  username)
        print("password = ", password)

        users = User.objects.filter(username=username)
        print(f"Found {users.count()} users with username '{username}'")

        for u in users:
            print(f"User {u.pk}: is_active={u.is_active}, password={u.password}")
            print(f"Password valid? {u.check_password(password)}")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            print("Login successful!")
            return HttpResponseRedirect("/")  # or redirect wherever you want
        else:
            print("Authentication failed")
        form = AuthenticationRememberMeForm(data=request.POST)

        # from google.cloud import datastore
        #
        # # Connect to the local Datastore emulator
        # client = datastore.Client(project="ealpha-test-application")
        #
        # # Query all users from the "auth_user" kind
        # query = client.query(kind="auth_user")
        # users = list(query.fetch())
        #
        # # Print user data
        # for user in users:
        #     print(user)

        # client = datastore.Client()
        #
        # # Query all entities in auth_user kind
        # query = client.query(kind='auth_user')
        # users = list(query.fetch())
        #
        # print(f"Found {len(users)} users")
        print(form.errors)

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

# @never_cache
# def remember_me_login (
#     request,
#     redirect_field_name = REDIRECT_FIELD_NAME,
#     ):
#
#     """
#     Based on code cribbed from django/trunk/django/contrib/auth/views.py
#
#     Displays the login form with a remember me checkbox and handles the login
#     action.
#
#     """
#
#     from django.conf import settings
#     from django.http import HttpResponseRedirect
#
#     from src.remember_me.forms import AuthenticationRememberMeForm
#
#     redirect_to = request.POST.get ( redirect_field_name, '' )
#
#     if request.method == "POST":
#
#         form = AuthenticationRememberMeForm ( data = request.POST, )
#
#         if form.is_valid ( ):
#
#             # Light security check -- make sure redirect_to isn't garbage.
#
#             if not redirect_to or '//' in redirect_to or ' ' in redirect_to:
#
#                 redirect_to = settings.LOGIN_REDIRECT_URL
#
#             if not form.cleaned_data [ 'remember_me' ]:
#
#                 request.session.set_expiry ( 0 )
#
#             from django.contrib.auth import login
#
#             login ( request, form.get_user ( ) )
#
#             if request.session.test_cookie_worked ( ):
#
#                 request.session.delete_test_cookie ( )
#
#             user = User.objects.get(username=request.user)
#             spaces = SpaceAccess.objects.filter(user=user)
#             spaces = [s for s in spaces if s.space.title != user.username]
#
#             if len(spaces) == 0 and redirect_to != '/corporate/create_trial_account':
#                 redirect_to = '/corporate/no_space_info'
#
#             return HttpResponseRedirect ( redirect_to )
#
#     request.session.set_test_cookie ( )
#     # print("this .............")
#     return HttpResponseRedirect('/accounts/login/')

# remember_me_login = never_cache ( remember_me_login )

# from django.contrib.auth import REDIRECT_FIELD_NAME
# from django.views.decorators.cache import never_cache
# from src.lorepo.spaces.models import SpaceAccess
# from django.contrib.auth.models import User
#
#
# def remember_me_login (
#     request,
#     redirect_field_name = REDIRECT_FIELD_NAME,
#     ):
#
#     """
#     Based on code cribbed from django/trunk/django/contrib/auth/views.py
#
#     Displays the login form with a remember me checkbox and handles the login
#     action.
#
#     """
#
#     from django.conf import settings
#     from django.http import HttpResponseRedirect
#
#     from src.remember_me.forms import AuthenticationRememberMeForm
#
#     redirect_to = request.POST.get ( redirect_field_name, '' )
#
#     if request.method == "POST":
#
#         form = AuthenticationRememberMeForm ( data = request.POST, )
#
#         if form.is_valid ( ):
#
#             # Light security check -- make sure redirect_to isn't garbage.
#
#             if not redirect_to or '//' in redirect_to or ' ' in redirect_to:
#
#                 redirect_to = settings.LOGIN_REDIRECT_URL
#
#             if not form.cleaned_data [ 'remember_me' ]:
#
#                 request.session.set_expiry ( 0 )
#
#             from django.contrib.auth import login
#
#             login ( request, form.get_user ( ) )
#
#             if request.session.test_cookie_worked ( ):
#
#                 request.session.delete_test_cookie ( )
#
#             user = User.objects.get(username=request.user)
#             spaces = SpaceAccess.objects.filter(user=user)
#             spaces = [s for s in spaces if s.space.title != user.username]
#
#             if len(spaces) == 0 and redirect_to != '/corporate/create_trial_account':
#                 redirect_to = '/corporate/no_space_info'
#
#             return HttpResponseRedirect ( redirect_to )
#
#     request.session.set_test_cookie ( )
#
#     return HttpResponseRedirect('/accounts/login/')
#
# remember_me_login = never_cache ( remember_me_login )

# from django.contrib.auth import REDIRECT_FIELD_NAME, login
# from django.views.decorators.cache import never_cache
# from django.utils.http import url_has_allowed_host_and_scheme
# from django.http import HttpResponseRedirect
# from django.conf import settings
# from django.contrib.auth.models import User
# from src.lorepo.spaces.models import SpaceAccess
# from src.remember_me.forms import AuthenticationRememberMeForm
#

# @never_cache
# def remember_me_login(request, redirect_field_name=REDIRECT_FIELD_NAME):
#     """
#     Displays the login form with a remember me checkbox and handles login.
#     """
#     redirect_to = request.POST.get(redirect_field_name, '')
#
#     if request.method == "POST":
#         form = AuthenticationRememberMeForm(data=request.POST)
#
#         if form.is_valid():
#             user = form.get_user()
#
#             # Validate redirect URL
#             if not url_has_allowed_host_and_scheme(redirect_to, allowed_hosts={request.get_host()}):
#                 redirect_to = settings.LOGIN_REDIRECT_URL
#
#             # Handle session expiry based on 'remember me' option
#             if not form.cleaned_data.get('remember_me', False):
#                 request.session.set_expiry(0)
#
#             login(request, user)
#
#             # Filter spaces excluding user’s own username as space title
#             spaces = SpaceAccess.objects.filter(user=user).exclude(space__title=user.username)
#
#             if not spaces.exists() and redirect_to != '/corporate/create_trial_account':
#                 redirect_to = '/corporate/no_space_info'
#
#             return HttpResponseRedirect(redirect_to)
#
#     return HttpResponseRedirect('/accounts/login/')
# from django.shortcuts import render


# def remember_me_login(request, redirect_field_name=REDIRECT_FIELD_NAME):
#     redirect_to = request.POST.get(redirect_field_name, '')
#
#     if request.method == "POST":
#         form = AuthenticationRememberMeForm(data=request.POST)
#
#         if form.is_valid():
#             user = form.get_user()
#
#             # Validate redirect URL
#             if not url_has_allowed_host_and_scheme(redirect_to, allowed_hosts={request.get_host()}):
#                 redirect_to = settings.LOGIN_REDIRECT_URL
#
#             # Handle session expiry based on 'remember me' option
#             if not form.cleaned_data.get('remember_me', False):
#                 request.session.set_expiry(0)
#
#             login(request, user)
#
#             # Filter spaces excluding user’s own username as space title
#             spaces = SpaceAccess.objects.filter(user=user).exclude(space__title=user.username)
#
#             if not spaces.exists() and redirect_to != '/corporate/create_trial_account':
#                 redirect_to = '/corporate/no_space_info'
#
#             return HttpResponseRedirect(redirect_to)
#
#     else:
#         form = AuthenticationRememberMeForm()
#     return HttpResponseRedirect('/accounts/login/')
#     # return render(request, 'login.html', {'form': form})  # Use your actual login template
