from lorepo.permission.decorators import has_space_access
from lorepo.permission.models import Permission
from rest_framework.permissions import BasePermission


class GenericHasSpaceAccess(BasePermission):
    PERMISSION = None
    IS_COMPANY = False
    TOKEN_KEY = None

    def has_permission(self, request, view):
        is_called = [False]     # Trick for accessing outer scope

        @has_space_access(self.PERMISSION, self.IS_COMPANY, self.TOKEN_KEY)
        def check_call_function(*args, **kwargs):
            is_called[0] = True

        # If user doesn't have access then decorator will raise PermissionDenied exception.
        check_call_function(request, **view.kwargs)

        return is_called[0]


class HasEditAssetPermission(GenericHasSpaceAccess):
    PERMISSION = Permission.ASSET_EDIT
