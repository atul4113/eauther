from django.urls import path
from src.lorepo.newsletter.views import index, get_emails_async

urlpatterns = [
    path('', index),
    path('get_emails_async/<int:newsletter_email_id>/', get_emails_async),
]
