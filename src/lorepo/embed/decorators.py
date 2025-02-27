from src.lorepo.mycontent.models import Content
from django.shortcuts import get_object_or_404
from src.lorepo.spaces.util import get_space_for_content, get_space_access
from django.contrib.auth.models import User
from src.lorepo.permission.models import Permission

def check_is_public(fn):
    def _wrapper(request, *args, **kwargs):
        if 'content_id' in kwargs:
            content = Content.get_cached_or_404(id = kwargs['content_id'])
            space = get_space_for_content(content)
            sa = None
            
            if isinstance(request.user, User):
                sa = get_space_access(space, request.user)
            if not content.is_content_public(): 
                if (not sa and not request.user.is_superuser) or (sa and not sa.hasAccess(Permission.CONTENT_VIEW)):
                    from django.http import Http404
                    raise Http404
        return fn(request, *args, **kwargs)
    return _wrapper