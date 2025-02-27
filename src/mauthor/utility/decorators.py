from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from src.lorepo.spaces.util import is_space_owner
from django.core.exceptions import PermissionDenied

def company_admin(view_func):
    def _wrapper(request, *args, **kwargs):
        if request.user.is_superuser or is_space_owner(request.user.company, request.user):
            return view_func(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return _wrapper

class LoginRequiredMixin(object):
    """
        View mixin which requires user to be authenticated and redirects user to login page if needed
    """

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)