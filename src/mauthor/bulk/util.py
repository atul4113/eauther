import json
import os

from django.contrib.auth.models import User
from django.views.generic import TemplateView
from src.libraries.utility.environment import get_versioned_module
from src.libraries.utility.queues import trigger_backend_task
from src.lorepo.spaces.models import Space, UserSpacePermissions
from django.shortcuts import get_object_or_404, render
from src.lorepo.spaces.util import get_space_access, load_kids, get_cached_kids
from src.libraries.utility.redirect import get_redirect_url
from django.core.mail import mail_admins
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseNotFound


def build_project_tree(request, project_id, template):
    project = get_object_or_404(Space, pk=project_id)

    spaces = project.kids.filter(is_deleted=False)
    spaces = [space for space in spaces if get_space_access(space, request.user)]
    load_kids(spaces)
    publications = sorted(list(spaces), key=lambda space: space.title)

    return render(request, template, {'publications' : publications, 'project' : project, 'next_url' : get_redirect_url(request)})

class BulkUpdate(TemplateView):
    project_id = None
    permission = None
    run_context = 'frontend'


    def dispatch(self, request, *args, **kwargs):
        if self.run_context == "backend":
            if os.getenv('GAE_MODULE_NAME') == 'default':
                if not request.META['SERVER_SOFTWARE'].startswith('Development'):
                    return HttpResponseNotFound()
            request.user = get_object_or_404(User, pk = kwargs['user_id'])
        try:
            usp = UserSpacePermissions.get_cached_usp_for_user(request.user)
            permissions = usp.get_permissions_for_space(int(kwargs['project_id']))
            if permissions and self.permission in permissions:
                return super(BulkUpdate, self).dispatch(request,*args, **kwargs)
        except:
            import logging
            logging.exception("BulkUpdate Dispatch Error")
        if self.run_context == "backend":
            mail_admins('Unauthorized access',
                        'Unauthorized access to bulk update %s: user=%s, project=%s ' % (self.__class__.__name__,
                                                                                         kwargs['user_id'],
                                                                                         kwargs['project_id']))
            return HttpResponse("OK")
        raise PermissionDenied

    def post(self, request, *args, **kwargs):
        if self.run_context == 'frontend':
            return self.frontend_post(request,  *args, **kwargs)
        else:
            kwargs.update(json.loads(request.body))
            return self.backend_post(**kwargs)

    def get_context_data(self, **kwargs):
        try:
            project_id = self.kwargs['project_id']
            spaces = get_cached_kids(project_id)
            spaces = [space for space in spaces if get_space_access(space, self.request.user)]
            load_kids(spaces)
            publications = sorted(list(spaces), key=lambda space: space.title)
            kwargs['spaces'] = publications
            kwargs['project_id'] = project_id
        except:
            pass
        return kwargs

    def deffer_backend_post(self, project_id, **kwargs):
        trigger_backend_task(self.backend_url % (project_id, kwargs['user_id']), payload=json.dumps(kwargs), target=get_versioned_module('backup'), queue_name='backup')

