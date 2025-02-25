from django.urls import path
from .views import BasedViewRedirect

urlpatterns = [
    path('', BasedViewRedirect.as_view(), name='based_view_redirect'),
]
