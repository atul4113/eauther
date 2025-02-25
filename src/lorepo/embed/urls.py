from django.urls import path

from . import views

urlpatterns = [
    path('<int:content_id>/', views.mobile, name='mobile'),
    path('<int:content_id>/<int:version>/', views.mobile, name='mobile_version'),
    path('editor/<int:content_id>/', views.editor, name='editor'),
    path('corporate_embed/<int:content_id>/', views.corporate_embed, name='corporate_embed'),
    path('book/<int:content_id>/', views.book, name='book'),
    path('iframe/<int:content_id>/', views.iframe, name='iframe'),
]
