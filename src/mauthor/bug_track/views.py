from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from lorepo.mycontent.models import Content
from mauthor.bug_track.models import Bug
from mauthor.bug_track.forms import AddBugForm
from mauthor.bug_track.util import get_users_for_email
from libraries.utility.redirect import get_redirect_url
from lorepo.spaces.util import get_space_for_content, is_space_owner
from django.contrib import messages
from lorepo.public.util import send_message
from django.template import loader
from django.template.context import Context
from django.conf import settings
from lorepo.permission.decorators import has_space_access
from lorepo.permission.models import Permission
from lorepo.permission.util import verify_space_access


@has_space_access(Permission.BUGTRACK_ADD)
def add_bug(request, content_id):
    content = Content.get_cached_or_404(id=content_id)
    form = AddBugForm(request.POST)
    if form.is_valid():
        title = form.cleaned_data['title']
        description = form.cleaned_data['description']
        author = request.user
        bug = Bug(title=title, description=description, author=author, content=content)
        bug.save()
        _send_emails(bug)
        messages.success(request, "Bug %(title)s has been added." % locals())
        return form
    else:
        return form


def delete(request, bug_id):
    bug = get_object_or_404(Bug, pk=bug_id)
    space = get_space_for_content(bug.content)
    if not is_space_owner(space, request.user):
        raise Http404
    messages.success(request, "Bug %(title)s has been deleted." % {'title': bug.title})
    content_id = bug.content.id
    back_url = get_redirect_url(request)
    bug.delete()
    return HttpResponseRedirect('/corporate/view/%(content_id)s?next=%(back_url)s' % {'content_id': content_id, 'back_url': back_url})


def _send_emails(bug):
    context = Context({'bug': bug, 'settings': settings})
    email = loader.get_template('emails/bug_track.txt')
    space = get_space_for_content(bug.content)
    users = get_users_for_email(space)
    emails = [user.email for user in users if verify_space_access(space, user, Permission.BUGTRACK_VIEW)]
    rendered = email.render(context)
    send_message(settings.SERVER_EMAIL, emails, "Message from %s bug track." % settings.APP_NAME, rendered)
