from django.urls import path
from src.lorepo.home import views

urlpatterns = [
    path('unpack_website/<int:website_id>/', views.unpack_website, name='unpack_website'),
]
