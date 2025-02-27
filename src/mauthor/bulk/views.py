from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from src.lorepo.mycontent.lesson.update_content_template import update_content_template
from src.lorepo.mycontent.models import UpdateTemplateStatus, ContentType, Content
from src.mauthor.bulk.util import BulkUpdate
from django.contrib import messages
from django.core.mail import mail_admins
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from src.mauthor.backup.views import get_contents
from src.lorepo.spaces.models import Space
from src.lorepo.mycontent.util import clean_content_assets,\
     get_contents_from_specific_space
from django.template.context import Context
from django.template import loader
from src.lorepo.public.util import send_message
from django.conf import settings

from src.lorepo.permission.models import Permission


def send_notification(user, project, skipped_contents, template, subject):
    context = Context({'skipped_contents': skipped_contents, 'user': user, 'project': project, 'settings': settings})
    email = loader.get_template(template)
    emails = [user.email]
    rendered = email.render(context)
    send_message(settings.SERVER_EMAIL, emails, subject, rendered)


def send_failure_notification(user, project, template, subject):
    context = Context({'user': user, 'project': project, 'settings': settings})
    email = loader.get_template(template)
    emails = [user.email]
    rendered = email.render(context)
    send_message(settings.SERVER_EMAIL, emails, subject, rendered)


class AssetsBulkUpdate(BulkUpdate):
    template_name = 'bulk/select_publications_for_assets.html'
    next_url = '/corporate/divisions'
    permission = Permission.BULK_ASSETS_UPDATE
    backend_url = '/bulk/backend/assets/%s/%s'

    def frontend_post(self, request, project_id):
        try:
            spaces = request.POST.getlist('spaces')
            if len(spaces):
                self.deffer_backend_post(project_id=project_id, user_id = request.user.id, spaces = spaces)
                messages.info(request, 'Lessons scheduled for bulk assets update. Once the update is ready you will be notified via email.')
        except Exception:
            import logging
            logging.exception("Error in Update Assets:")
            return HttpResponseBadRequest()
        return HttpResponseRedirect(self.next_url)

    def backend_post(self, project_id, user_id, spaces):
        try:
            user = get_object_or_404(User, pk=user_id)
            project = get_object_or_404(Space, pk=project_id)
            contents = get_contents(project, spaces)
            skipped_contents = []
            for content in contents:
                editing_user = content.who_is_editing()
                if editing_user is not None:
                    skipped_contents.append((content.id, content.title))
                    continue
                clean_content_assets(user, content)
            send_notification(user, project, skipped_contents, 'bulk/assets_confirmation.txt', 'Assets updated successfully')
        except:
            import logging
            logging.exception("Update assets fail:")
            import traceback
            mail_admins('Bulk update templates failed: user_id=%s, project_id=%s' % (user_id, project_id), traceback.format_exc())
            send_failure_notification(user, project, 'bulk/assets_failure.txt', 'Assets were not updated')
        return HttpResponse("OK")

class TemplateBulkUpdate(BulkUpdate):
    template_name = 'bulk/template_job_form.html'
    next_url = '/corporate/divisions'
    permission = Permission.BULK_TEMPLATE_UPDATE
    backend_url = '/bulk/backend/templates/%s/%s'


    def frontend_post(self, request, project_id):
        try:
            spaces = request.POST.getlist('spaces')
            new_template = request.POST.get('new_template', False)
            preferences = request.POST.getlist('preferences')

            if new_template:
                new_template = request.POST['template']
            if len(spaces):
                if new_template:
                    self.deffer_backend_post(project_id=project_id,
                                            user_id = request.user.id,
                                            spaces = spaces,
                                            preferences = preferences,
                                            template_id = new_template)
                else:
                    self.deffer_backend_post(project_id=project_id,
                                            user_id = request.user.id,
                                            preferences = preferences,
                                            spaces = spaces)
                messages.info(request, 'Lessons scheduled for bulk template update. Once the update is ready you will be notified via email.')
        except Exception:
            import logging
            logging.exception("Error in Update Templates:")
            return HttpResponseBadRequest()
        return HttpResponseRedirect(self.next_url)


    def backend_post(self, project_id, user_id, spaces, preferences, template_id=None):
        try:
            user = get_object_or_404(User, pk=user_id)
            project = get_object_or_404(Space, pk=project_id)
            if not template_id: #for template update get
                contents = get_contents(project, spaces)
            else: #template replacement is not recursive nor propagated up the space hierarchy
                contents = []
                for space_id in spaces:
                    content_filter = lambda content: not content.is_deleted and content.content_type == ContentType.LESSON
                    contents += get_contents_from_specific_space(space_id, content_filter=content_filter)
            skipped_contents = []
            template = None
            if template_id:
                template = Content.get_cached(id = template_id)
            for content in contents:
                result = update_content_template(content, user, preferences, template_content=template)
                if result == UpdateTemplateStatus.CONTENT_CURRENTLY_EDITED:
                    skipped_contents.append((content.id, content.title, False))
                if result == UpdateTemplateStatus.TEMPLATE_CURRENTLY_EDITED:
                    if template_id:
                        skipped_contents.append((content.id, content.title, template))
                    else:
                        template_skipped = content.get_template()
                        template_skipped_title = 'N/A'
                        if template_skipped:
                            template_skipped_title = template_skipped.title
                        skipped_contents.append((content.id, content.title, template_skipped_title))
            send_notification(user, project, skipped_contents, 'bulk/templates_confirmation.txt', "Templates successfully updated")
        except Exception:
            import logging
            logging.exception("Update template fail:")
            import traceback
            mail_admins('Bulk update templates failed: user_id=%s, project_id=%s' % (user_id, project_id), traceback.format_exc())
            send_failure_notification(user, project, 'bulk/templates_failure.txt', "Templates were not updated")
        return HttpResponse("OK")