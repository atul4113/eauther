from django.urls import path
from src.mauthor.company import views

urlpatterns = [
    path('list_companies/', views.companies_report),
    path('remove_company_from_test/', views.remove_company_from_test),
    path('details/<int:space_id>/', views.details),
    path('edit/<int:space_id>/', views.edit_details),
    path('edit_locale/<int:space_id>/', views.edit_locale),
    path('lock/<int:space_id>/', views.lock),
    path('unlock/<int:space_id>/', views.unlock),
]
