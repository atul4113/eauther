from django.urls import path

from .views import PermissionPanelView
from .api import RoleView, ProjectsView, ProjectsUserView, PermissionUserView, PermissionEditUserView, \
    DeleteRoleView, PermissionDeleteUserView, PermissionDeleteUserPermissionView

urlpatterns = [
    # Views
    path('', PermissionPanelView.as_view(), name='permission_panel'),

    # API Endpoints
    path('api/role/<int:role_id>/', RoleView.as_view(), name='role_detail'),
    path('api/role/delete/<int:role_id>/', DeleteRoleView.as_view(), name='role_delete'),
    path('api/role/', RoleView.as_view(), name='role_list'),
    path('api/projects/company_user/<int:company_user_id>/', ProjectsView.as_view(), name='projects_by_company_user'),
    path('api/projects/project/<int:project_id>/', ProjectsUserView.as_view(), name='projects_by_project_id'),
    path('api/user/permissions/', PermissionUserView.as_view(), name='user_permissions'),
    path('api/user/edit/permissions/', PermissionEditUserView.as_view(), name='edit_user_permissions'),
    path('api/user/delete/permissions/', PermissionDeleteUserPermissionView.as_view(), name='delete_user_permissions'),
    path('api/delete/company_user/', PermissionDeleteUserView.as_view(), name='delete_company_user'),
]
