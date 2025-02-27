import json
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.safestring import mark_safe
from django.views.generic.base import TemplateView


from src.lorepo.corporate.decorators import HasSpacePermissionMixin
from src.lorepo.spaces.util import has_space_permission
from src.lorepo.permission.models import Role, Permission
from src.lorepo.permission.util import translate_perm_to_tuple,\
    group_permissions_tuples, get_company_users, get_projects_users, get_projects_and_publications
from src.lorepo.permission.decorators import has_space_access

permissions_levels = {'project_level_only' : ['Manage Courses'],
    'company_level_only' : ['Upload Company Logo', 'View Company Details', 'Edit Company Details', 'View Company Administration Panel']
}

# noinspection PyMethodMayBeStatic
class PermissionPanelView(HasSpacePermissionMixin, TemplateView):
    permission = Permission.SPACE_ACCESS_MANAGE
    is_company = True
    template_name = 'permission/managment_panel.html'
    permissions_levels = {'project_level_only': ['Manage Courses'],
                          'company_level_only': ['Upload Company Logo', 'View Company Details', 'Edit Company Details',
                                                 'View Company Administration Panel']
                          }

    def get_context_data(self, **kwargs):
        projects, _ = get_projects_and_publications(self.request.user, self.request.user.company)
        company_users, is_company_admin = self.get_company_users(projects)

        return {
            "roles": self._parse_for_javascript(self.get_roles()),
            "projects": self._parse_for_javascript(self.get_projects_data(projects)),
            "company": self._parse_for_javascript(self.get_company_data()),
            "permissions_level": self._parse_for_javascript(permissions_levels),
            "permissions": self._parse_for_javascript(self.get_permissions()),
            "company_users": self._parse_for_javascript(company_users),
            "is_company_admin": self._parse_for_javascript(is_company_admin)
        }

    def get_company_users(self, projects):
        is_company_admin = has_space_permission(self.request.user.company, self.request.user, 'SPACE_ACCESS_MANAGE')
        corporate_users = get_company_users(self.request.user.company) if is_company_admin else get_projects_users(self.request.user.company, projects)

        return [{"id": cu.id, "name": cu.user.username, "userid": cu.user.id} for cu in corporate_users], is_company_admin

    def get_permissions(self):
        permissions_tuples = [translate_perm_to_tuple(perm) for perm in Permission().get_all()]
        permissions = group_permissions_tuples(permissions_tuples)

        permissions = [{"name": key, "permissions": value} for key, value in list(permissions.items())]
        permissions.sort(key=lambda element: element["name"])
        return permissions

    def get_company_data(self):
        company, user = self.request.user.company, self.request.user
        if has_space_access(company, user, 'SPACE_ACCESS_MANAGE'):
            return {
                "id": company.id,
                "name": company.title,
                "have": True
            }
        else:
            return {
                "have": False
            }

    def _parse_for_javascript(self, value):
        return mark_safe(json.dumps(value))

    def get_roles(self):
        return [{"id": role.id, "name": role.name} for role in Role.objects.filter(company=self.request.user.company).order_by('name')]

    def get_projects_data(self, projects):
        projects = [{"id": project.id, "name": project.title, "publications": self.get_publications(project.publications)} for project in projects]

        return projects

    def get_publications(self, publications):
        non_parsed_publications = publications if publications else None
        parsed_publications = []
        if non_parsed_publications is not None:
            parsed_publications = [{"id": publication.id, "name": publication.title} for publication in non_parsed_publications]

        return parsed_publications