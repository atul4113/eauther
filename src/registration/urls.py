# URLConf for Django user registration and authentication.

from django.urls import re_path, path
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from registration.views import activate, register
from src.remember_me.views import remember_me_login  # Import the actual function

urlpatterns = [
    # Activation keys get matched by \w+ instead of the more specific
    # [a-fA-F0-9]{40} because a bad activation key should still get to the view;
    # that way it can return a sensible "invalid key" message instead of a confusing 404.
    re_path(r'^activate/(?P<activation_key>\w+)/$', activate, name='registration_activate'),

    # Custom login view (if necessary)
    path('login/', remember_me_login, name='remember_me_login'),

    # Auth views (logout, password change, reset, etc.)
    path('logout/', auth_views.LogoutView.as_view(template_name='registration/logout.html'), name='auth_logout'),
    path('password/change/', auth_views.PasswordChangeView.as_view(), name='auth_password_change'),
    path('password/change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('password/reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    re_path(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password/reset/complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('password/reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),

    # Registration views
    path('register/', register, name='registration_register'),
    path('register/complete/', TemplateView.as_view(template_name='registration/registration_complete.html'), name='registration_complete'),
]
