from class_views.ApiView import ApiView
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from libraries.utility.cacheproxy import delete_template_fragment_cache
from libraries.utility.helpers import get_object_or_none
from lorepo.corporate.decorators import HasSpacePermissionMixin
from lorepo.corporate.models import CompanyUser
from lorepo.corporate.signals import access_rights_changed, company_structure_changed
from lorepo.permission.api_utils import get_error_message
from lorepo.permission.models import Role, Permission
from lorepo.permission.api_utility import get_filtered_publication_data, get_project_data
from lorepo.permission.util import translate_perm_to_tuple, group_permissions_tuples, \
    translate_perm_to_integer, get_company_for_user, create_company_user, remove_company_user
from lorepo.spaces.form import AccessForm
from lorepo.spaces.model.companyspacemap.company_space_map import CompanySpaceMap
from lorepo.spaces.model.companyspacemap.multitasks_locker import CompanySpaceMapTaskLocker
from lorepo.spaces.models import SpaceAccess, Space
from mauthor.utility.decorators import LoginRequiredMixin


# noinspection PyMethodMayBeStatic
class RoleView(LoginRequiredMixin, HasSpacePermissionMixin, ApiView):
    permission = Permission.SPACE_ACCESS_MANAGE
    is_company = True

    ERROR_ROLE_DOES_NOT_EXISTS = "Selected role does not exists."
    ERROR_ROLE_NAME_EMPTY = "User have to type role name."
    ERROR_NO_PERMISSIONS = "User have to type permissions."

    def get(self, request, role_id, *args, **kwargs):
        role = get_object_or_none(Role, id=role_id)
        if Role is None:
            return get_error_message(404, self.ERROR_ROLE_DOES_NOT_EXISTS)

        return {
            "status": 200,
            "role_permissions": self.get_role_permissions(role)
        }

    def post(self, request, role_id=None, *args, **kwargs):
        is_edit_role = True if role_id is not None else False
        validated_data = self.validate_data(is_edit_role)

        if validated_data["is_valid"] == False:
            return validated_data

        role_name = validated_data["name"]
        permissions = validated_data["permissions"]

        if role_id is None:
            return self.add_role(role_name, permissions)
        else:
            return self.edit_role(role_id, permissions)

    def validate_data(self, is_edit_role):
        role_name = self.request.POST.get('name', default=None)
        permissions = self.request.POST.getlist('permissions[]')

        if not is_edit_role and (role_name is None or role_name.strip() == ""):
            return get_error_message(400, self.ERROR_ROLE_NAME_EMPTY)

        if permissions is None or len(permissions) == 0:
            return get_error_message(400, self.ERROR_NO_PERMISSIONS)

        return {
            "is_valid": True,
            "name": role_name,
            "permissions": permissions
        }

    def get_role_permissions(self, role):
        permissions_tuples = [translate_perm_to_tuple(perm) for perm in role.permissions]
        permissions = group_permissions_tuples(permissions_tuples)

        result = {}
        for key, value in list(permissions.items()):
            result[key] = {}
            for item in value:
                result[key][item] = True
        return result

    def add_role(self, role_name, role_permissions):
        permissions = [translate_perm_to_integer(perm) for perm in role_permissions]

        role = Role(name=role_name, company=self.request.user.company, permissions=permissions)
        role.save()

        return {
            "status": 200,
            "message": "Role added succesfully.",
            "role_id": role.id,
            "role_permissions": self.get_role_permissions(role)
        }

    def edit_role(self, role_id, role_permissions):
        role = get_object_or_none(Role, id=role_id)
        if role is None:
            return get_error_message(400, self.ERROR_ROLE_DOES_NOT_EXISTS)

        permissions = [translate_perm_to_integer(perm) for perm in role_permissions]
        role.permissions = permissions
        role.save()

        return {
            "status": 200,
            "message": "Role edited with success.",
            "role_id": role.id,
            "role_permissions": self.get_role_permissions(role)
        }


# noinspection PyMethodMayBeStatic
class DeleteRoleView(LoginRequiredMixin, HasSpacePermissionMixin, ApiView):
    is_company = True
    permission = Permission.SPACE_ACCESS_MANAGE

    def post(self, request, role_id, *args, **kwargs):
        role = Role.objects.get(id=role_id)
        if SpaceAccess.objects.filter(roles=int(role_id)).count() > 0:
            return {
                "status": 400,
                "message": 'One or more users has role {0} assigned. Please remove access first.'.format(role.name)
            }
        else:
            role_name = role.name
            role.delete()
            return {
                "status": 200,
                "message": 'Role {0} has been removed.'.format(role_name)
            }


# noinspection PyMethodMayBeStatic
class ProjectsView(LoginRequiredMixin, ApiView):
    def get(self, request, company_user_id, *args, **kwargs):
        filtered_spaces, space_access_dict = self.filter_space_accesses_for_company_user(company_user_id)
        result = self.prepare_projects_data(filtered_spaces, space_access_dict)

        return result

    def prepare_projects_data(self, filtered_spaces, space_access_dict):
        if filtered_spaces is None and space_access_dict is None:
            return {
                "isCalculating": True
            }

        result = {
            "isCalculating": False,
            "company": filtered_spaces["company"],
            "projects": [],
            "publications": []
        }

        if result["company"] is not None:
            data = get_project_data(result["company"][2], result["company"][0], space_access_dict)

            result["projects"].append(data)

        for project_id, _, child_list in filtered_spaces["projects"]:
            data = get_project_data(child_list, project_id, space_access_dict)

            result["projects"].append(data)

        result["publications"] = [get_filtered_publication_data(x, space_access_dict) for x in filtered_spaces["publications"]]

        return result

    def filter_space_accesses_for_company_user(self, company_user_id):
        company_user = CompanyUser.objects.get(pk=company_user_id)
        space_access_objects = SpaceAccess.objects.filter(user=company_user.user)

        company_space_map_cache = CompanySpaceMap.is_in_cache(company_user.company.id)
        if not company_space_map_cache:
            CompanySpaceMapTaskLocker(company_user.company.id).trigger()

            return None, None
        company_space_map = CompanySpaceMap()
        company_space_map._parse(company_space_map_cache)
        space_access_dict = {}

        for sa in space_access_objects:
            space_access_dict[sa.space.id] = sa

        space_accesses_ids_set = set(space_access_dict)

        filtered_spaces = {
            "company": None,
            "projects": [],
            "publications": []
        }

        for csm_tuple in list(company_space_map.space_dict.values()):
            if csm_tuple[1] is None:
                filtered_spaces["company"] = csm_tuple if csm_tuple[0] in space_accesses_ids_set else None
                continue

            if csm_tuple[0] in space_accesses_ids_set:
                if space_access_dict[csm_tuple[0]].space.is_publication():
                    filtered_spaces["publications"].append(csm_tuple)
                else:
                    filtered_spaces["projects"].append(csm_tuple)

        return filtered_spaces, space_access_dict


# noinspection PyMethodMayBeStatic
class ProjectsUserView(LoginRequiredMixin, ApiView):

    ERROR_PROJECT_DOES_NOT_EXISTS = "Requested project does not exists"

    def get(self, request, project_id, *args, **kwargs):
        project_space = get_object_or_none(Space, id=project_id)
        if project_space is None:
            return get_error_message(404, self.ERROR_PROJECT_DOES_NOT_EXISTS)

        publications_data = self.get_publications_data(project_id)

        project_space_accesses = SpaceAccess.objects.filter(space=project_id)

        result = {
            "status": 200,
            "id": project_id,
            "name": project_space.title,
            "project_users": [{
                                  "id": space_access.user.id,
                                  "name": space_access.user.username,
                                  "actual_roles": self.get_roles_from_space_access(space_access)
                              } for space_access in project_space_accesses],
            "publications": publications_data
        }

        return result

    def get_publications_data(self, project_id):
        def get_space_data(data_tuple):
            space, space_accesses = data_tuple
            return {
                "id": space.id,
                "name": space.title,
                "users": [{
                              "id": space_access.user.id,
                              "name": space_access.user.username,
                              "actual_roles": self.get_roles_from_space_access(space_access)
                          } for space_access in space_accesses]
            }

        data_tuples = [(publication, SpaceAccess.objects.filter(space=publication.id)) for publication in Space.objects.filter(parent=project_id)]
        return list(map(get_space_data, data_tuples))

    def get_roles_from_space_access(self, space_access):
        return [{
                    "id": role.id,
                    "name": role.name,
                } for role in [Role.get_cached_role(role_id) for role_id in space_access.roles]]


# noinspection PyMethodMayBeStatic
class PermissionUserView(HasSpacePermissionMixin, LoginRequiredMixin, ApiView):
    permission = Permission.SPACE_ACCESS_MANAGE
    is_company = True
    edit_mode = False

    ERROR_MESSAGE_NO_ROLES = 'You need to establish at least one role if you want to add an access.'
    ERROR_MESSAGE_USER_IN_OTHER_COMPANY = 'User {0} has already access to other company.'

    def post(self, request, *args, **kwargs):
        validated_input = self.validate_input()

        if validated_input["is_valid"]:
            output = self.execute(validated_input)
        else:
            output = validated_input

        return output

    def execute(self, data):
        space_access = self.get_space_access(data)
        space_access.save()
        company_user, _ = create_company_user(self.request.user.company, data["user"])
        company_structure_changed.send(None, company_id=self.request.user.company.id, user_id=self.request.user.id)
        access_rights_changed.send(self.request.user, user_id=data["user"].id)
        delete_template_fragment_cache('menu', data["user"])

        return {
            "message": 'Access for user {0} to project/publication {1} has been added.'.format(data["user"], data["space"]),
            "status": 200,
            "company_user_id": company_user.id,
            "company_username": company_user.username,
            "user_id": company_user.user.id
        }

    def get_space_access(self, data):
        if not self.edit_mode:
            return SpaceAccess(user=data["user"], space=data["space"], roles=data["roles"])
        else:
            space_access, _ = SpaceAccess.objects.get_or_create(user=data["user"], space=data["space"])
            space_access.roles = data["roles"]
            return space_access

    def validate_input(self):
        if not CompanySpaceMap.is_in_cache(self.request.user.company.id):
            CompanySpaceMapTaskLocker(self.request.user.company.id).trigger()
            return get_error_message(202, "User access rights are recalculated - this might take several minutes")
        form = self.get_access_form()
        roles_ids_list = self.request.POST.getlist('roles[]')
        if len(roles_ids_list) == 0:
            return get_error_message(400, self.ERROR_MESSAGE_NO_ROLES)
        elif form.is_valid():
            username = form.cleaned_data['user']
            user = get_object_or_404(User, username=username)
            user_company = get_company_for_user(user)
            if user_company and user_company.id != self.request.user.company.id:
                return get_error_message(400, self.ERROR_MESSAGE_USER_IN_OTHER_COMPANY.format(user))
            else:
                return {
                    "is_valid": True,
                    "user": user,
                    "user_company": user_company,
                    "roles": [int(role) for role in roles_ids_list],
                    "space": get_object_or_404(Space, pk=form.cleaned_data['space'])
                }
        else:
            errors = ""
            if '__all__' in form.errors:
                errors = form.errors['__all__'][0]
            else:
                for key, value in list(form.errors.items()):
                    errors = "{0}".format(value)
                    break

            return get_error_message(400, errors)

    def get_access_form(self):
        form = AccessForm(self.request.POST)
        form.set_edit_mode(self.edit_mode)
        form.set_company_id(self.request.user.company.id)
        return form


# noinspection PyMethodMayBeStatic
class PermissionEditUserView(PermissionUserView):
    edit_mode = True


class PermissionDeleteUserPermissionView(LoginRequiredMixin, HasSpacePermissionMixin, ApiView):
    is_company = True
    permission = Permission.SPACE_ACCESS_MANAGE

    ERROR_USER_CANT_DELETE_HIS_OWN_PERMISSIONS = "User can't delete his own permissions."
    ERROR_COMPANY_USER_DOES_NOT_EXISTS = "Company user does not exists."
    ERROR_SPACE_ACCESS_DOES_NOT_EXISTS = "Space access to project/publication does not exists."

    def post(self, request, *args, **kwargs):
        company_user_id = self.request.POST.get("user_id")
        space_id = self.request.POST.get("space_id")
        company_user = get_object_or_none(CompanyUser, id=company_user_id)
        if company_user is None:
            return get_error_message(400, self.ERROR_COMPANY_USER_DOES_NOT_EXISTS)

        user = company_user.user
        if self.request.user.id == user.id:
            return get_error_message(400, self.ERROR_USER_CANT_DELETE_HIS_OWN_PERMISSIONS)

        space_access = get_object_or_none(SpaceAccess, user=user.id, space=space_id)
        if space_access is None:
            return get_error_message(400, self.ERROR_SPACE_ACCESS_DOES_NOT_EXISTS)

        space = space_access.space

        space_access.delete()

        company_structure_changed.send(None, company_id=request.user.company.id, user_id=request.user.id)
        access_rights_changed.send(request.user, user_id=user.id)
        delete_template_fragment_cache('menu', user)

        return {
            "status": 200,
            "message": 'Access for user %(user)s to project/publication %(space)s has been removed.' % locals()
        }


class PermissionDeleteUserView(LoginRequiredMixin, HasSpacePermissionMixin, ApiView):
    is_company = True
    permission = Permission.SPACE_ACCESS_MANAGE

    ERROR_COMPANY_USER_DOES_NOT_EXISTS = "Company user does not exists."
    ERROR_USER_CANT_DELETE_HISMSELF = "User can't delete himself."

    def post(self, request, *args, **kwargs):
        company_user_id = self.request.POST.get("company_user_id")
        company_user = get_object_or_none(CompanyUser, id=company_user_id)
        if company_user is None:
            return get_error_message(400, self.ERROR_COMPANY_USER_DOES_NOT_EXISTS)

        user = company_user.user
        if self.request.user.id == user.id:
            return get_error_message(400, self.ERROR_USER_CANT_DELETE_HISMSELF)

        remove_company_user(request.user.company, company_user.user, company_user)

        company_structure_changed.send(None, company_id=request.user.company.id, user_id=request.user.id)
        access_rights_changed.send(request.user, user_id=user.id)
        delete_template_fragment_cache('menu', user)

        return {
            "status": 200,
            "message": 'User {0} has been removed from company.'.format(company_user.user.username)
        }
