from django.urls import path
from libraries.proxy.views import get

urlpatterns = [
    path('get/', get),
]
