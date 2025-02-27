from django.urls import path
from src.libraries.proxy.views import get

urlpatterns = [
    path('get/', get),
]
