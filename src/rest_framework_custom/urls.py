from django.urls import re_path

from django.contrib.auth import views as auth_views

app_name = 'rest_framework_custom'  # ✅ this is the namespace
urlpatterns = [
    re_path(r'^login/$', auth_views.LoginView.as_view(template_name='rest_framework_custom/login.html'), name='login'),
    re_path(r'^logout/$', auth_views.LogoutView.as_view(), name='logout'),
    re_path(r'^password_reset/$', auth_views.PasswordResetView.as_view(), name='password_reset'),
]