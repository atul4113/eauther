from django.shortcuts import get_object_or_404
from lorepo.mycontent.models import Content
from lorepo.spaces.models import Space, SpaceAccess
from lorepo.spaces.util import get_space_for_content, is_space_owner, is_company_locked
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from lorepo.corporate.templatetags.corporate import is_any_division_admin
from lorepo.permission.util import check_space_access
from lorepo.course.models import Course
from lorepo.token.util import generate_token
from django.http import HttpResponseRedirect

def has_space_access(permission, is_company=False, token_key=None):
    def _outer(fn):
        def _inner(request, *args, **kwargs):
            if isinstance(request.user, AnonymousUser):
                raise PermissionDenied

            if request.user.is_superuser:
                return fn(request, *args, **kwargs)

            session_key = 'security_token_%s' % token_key
            if session_key in request.session and str(request.session[session_key]) == request.GET.get('_SECURITY_TOKEN'):
                return fn(request, *args, **kwargs)

            for key in ['content_id', 'addon_id']:
                if key in kwargs:
                    content = Content.get_cached_or_404(id = kwargs[key])
                    space = get_space_for_content(content)
                    check_space_access(space, request.user, permission)

            for key in ['space_id', 'project_id']:
                if key in kwargs:
                    space = get_object_or_404(Space, pk = kwargs[key])
                    check_space_access(space, request.user, permission)
                    request.kwargs = {}
                    request.kwargs['space'] = space

            if 'course_id' in kwargs:
                course = get_object_or_404(Course, pk = kwargs['course_id'])
                space = course.project
                check_space_access(space, request.user, permission)

            if is_company:
                if not request.user.company:
                    raise PermissionDenied
                if not is_space_owner(request.user.company, request.user) and not is_any_division_admin(request.user):
                  
                    raise PermissionDenied

            if 'spaceaccess_id' in kwargs:
                space_access = get_object_or_404(SpaceAccess, pk = kwargs['spaceaccess_id'])
                check_space_access(space_access.space, request.user, permission)

            return fn(request, *args, **kwargs)
        return _inner
    return _outer


def security_token(key):
    def _inner(function):
        session_key = 'security_token_%s' % key
        def _wrapper(request, *args, **kwargs):
            if not session_key in request.session:
                request.session[session_key] = generate_token()
            return function(request, *args, **kwargs)
        return _wrapper
    return _inner


def company_locked(fn):
    def wrapped(request, *args, **kwargs):
        if is_company_locked(request.user.company):
            return HttpResponseRedirect('/corporate')
        else:
            return fn(request, *args, **kwargs)
    return wrapped