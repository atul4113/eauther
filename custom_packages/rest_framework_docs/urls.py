from django.urls import path
from .views import documentation

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = [
    path("", documentation, name="api-documentation"),
]
