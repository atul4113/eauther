from django.urls import path
from lorepo.cron import views  # Import views module

urlpatterns = [
    path('keepalive', views.keepalive),
    path('delete_old_courses', views.delete_old_courses),
    path('delete_old_courses_cron', views.delete_old_courses_cron),
    path('delete_old_courses_async', views.delete_old_courses_async),
    path('lock_companies', views.lock_companies),
    path('lock_companies_cron', views.lock_companies_cron),
    path('lock_companies_async', views.lock_companies_async),
    path('is_more_users_in_company', views.is_more_users_in_company),
    path('is_more_users_in_company_cron', views.is_more_users_in_company_cron),
    path('is_more_users_in_company_async', views.is_more_users_in_company_async),
]
