from django.conf.urls import patterns
from lorepo.permission.api import RoleView, ProjectsView, ProjectsUserView, PermissionUserView, PermissionEditUserView, \
    DeleteRoleView, PermissionDeleteUserView, PermissionDeleteUserPermissionView
from lorepo.permission.views import PermissionPanelView

urlpatterns = patterns('lorepo.permission.views',
    (r'^$', PermissionPanelView.as_view()),
)

urlpatterns += patterns('lorepo.permission.api',
    (r'^api/role/(?P<role_id>\d+)', RoleView.as_view()),
    (r'^api/role/delete/(?P<role_id>\d+)', DeleteRoleView.as_view()),
    (r'^api/role/', RoleView.as_view()),
    (r'^api/projects/company_user/(?P<company_user_id>\d+)', ProjectsView.as_view()),
    (r'^api/projects/project/(?P<project_id>\d+)', ProjectsUserView.as_view()),
    (r'^api/user/permissions/', PermissionUserView.as_view()),
    (r'^api/user/edit/permissions/', PermissionEditUserView.as_view()),
    (r'^api/user/delete/permissions/', PermissionDeleteUserPermissionView.as_view()),
    (r'^api/delete/company_user/', PermissionDeleteUserView.as_view()),
)