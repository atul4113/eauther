"""
Login and logout views for the browsable API.

Add these to your root URLconf if you're using the browsable API and
your API requires authentication:

    urlpatterns = [
        ...
        url(r'^auth/', include('rest_framework_custom.urls', namespace='rest_framework_custom'))
    ]

In Django versions older than 1.9, the urls must be namespaced as 'rest_framework_custom',
and you should make sure your authentication settings include `SessionAuthentication`.
"""


from django.conf.urls import url
from django.contrib.auth import views

template_name = {'template_name': 'rest_framework_custom/login.html'}

app_name = 'rest_framework_custom'
urlpatterns = [
    url(r'^login/$', views.login, template_name, name='login'),
    url(r'^logout/$', views.logout, template_name, name='logout'),
]
