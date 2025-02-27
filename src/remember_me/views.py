from django.contrib.auth import REDIRECT_FIELD_NAME
from django.views.decorators.cache import never_cache
from src.lorepo.spaces.models import SpaceAccess
from django.contrib.auth.models import User


def remember_me_login (
    request,
    redirect_field_name = REDIRECT_FIELD_NAME,
    ):

    """
    Based on code cribbed from django/trunk/django/contrib/auth/views.py
    
    Displays the login form with a remember me checkbox and handles the login
    action.
    
    """
    
    from django.conf import settings
    from django.http import HttpResponseRedirect

    from src.remember_me.forms import AuthenticationRememberMeForm
    
    redirect_to = request.REQUEST.get ( redirect_field_name, '' )
    
    if request.method == "POST":
    
        form = AuthenticationRememberMeForm ( data = request.POST, )
        
        if form.is_valid ( ):
        
            # Light security check -- make sure redirect_to isn't garbage.
            
            if not redirect_to or '//' in redirect_to or ' ' in redirect_to:
            
                redirect_to = settings.LOGIN_REDIRECT_URL
                
            if not form.cleaned_data [ 'remember_me' ]:
            
                request.session.set_expiry ( 0 )
                
            from django.contrib.auth import login
            
            login ( request, form.get_user ( ) )
            
            if request.session.test_cookie_worked ( ):
            
                request.session.delete_test_cookie ( )

            user = User.objects.get(username=request.user)
            spaces = SpaceAccess.objects.filter(user=user)
            spaces = [s for s in spaces if s.space.title != user.username]

            if len(spaces) == 0 and redirect_to != '/corporate/create_trial_account':
                redirect_to = '/corporate/no_space_info'

            return HttpResponseRedirect ( redirect_to )

    request.session.set_test_cookie ( )

    return HttpResponseRedirect('/accounts/login/')

remember_me_login = never_cache ( remember_me_login )
