from src.lorepo.mycontent.models import Content
from src.lorepo.public.util import send_message
from django.template.context import Context
from django.template import loader
from django.conf import settings

def send_export_failure_notification(user, content_id):
    content = Content.get_cached(id=content_id)
    subject = 'Xliff document for presentation ' + content.title + ' has NOT been exported.'
    context = Context({ 'app_name' : settings.APP_NAME,
                        'subject' : subject })
    email = loader.get_template('localization/notifications/export_failure_notification.html')
    rendered = email.render(context)
    send_message(settings.SERVER_EMAIL, [user.email], subject, rendered)

def send_create_xliff_success_notification(user, content_id, project_id):
    content = Content.get_cached(id=content_id)
    subject = 'Lesson for localization has been created.'
    context = Context({'content': content, 'settings': settings, 'username': user.username, 'project_id': project_id})
    email = loader.get_template('localization/notifications/create_success_notification.html')
    rendered = email.render(context)
    send_message(settings.SERVER_EMAIL, [user.email], subject, rendered)
    
def send_create_xliff_failure_notification(user, content_id):
    content = Content.get_cached(id=content_id)
    subject = 'Lesson for localization has NOT been created.'
    context = Context({ 'content' : content, 'app_name' : settings.APP_NAME, 'username' : user.username })
    email = loader.get_template('localization/notifications/create_failure_notification.html')
    rendered = email.render(context)
    send_message(settings.SERVER_EMAIL, [user.email], subject, rendered)

def send_export_success_notification(user, content_id, uploaded_file_id):
    content = Content.get_cached(id=content_id)
    subject = 'Xliff document for presentation ' + content.title + ' has been exported.'
    context = Context({'uploaded_file_id': uploaded_file_id,
                        'settings': settings,
                        'subject': subject})
    email = loader.get_template('localization/notifications/export_success_notification.html')
    rendered = email.render(context)
    send_message(settings.SERVER_EMAIL, [user.email], subject, rendered)

def send_import_failure_notification(user, important_informations):
    subject = 'Presentation has NOT been created.'
    context = Context({ 'important_informations' : important_informations,
                        'app_name' : settings.APP_NAME,
                        'subject' : subject })
    email = loader.get_template('localization/notifications/import_failure_notification.html')
    rendered = email.render(context)
    send_message(settings.SERVER_EMAIL, [user.email], subject, rendered)

def send_import_success_notification(user, content_id, important_informations):
    content = Content.get_cached(id=content_id)
    subject = 'Presentation ' + content.title + ' has been created.'
    context = Context({ 'important_informations' : important_informations,
                        'settings' : settings,
                        'content_id' : content_id,
                        'subject' : subject })
    email = loader.get_template('localization/notifications/import_success_notification.html')
    rendered = email.render(context)
    send_message(settings.SERVER_EMAIL, [user.email], subject, rendered)
    
def send_content_too_big_notification(user, content):
    subject = 'Localized version for ' + content.title + ' has not been created.'
    context = Context({ 'app_name' : settings.APP_NAME,
                        'content' : content,
                        'subject' : subject,
                        'user' : user,
                        'pages' : list(zip(content.get_pages(), content.get_page_titles())) })
    email = loader.get_template('localization/notifications/content_too_big_notification.html')
    rendered = email.render(context)
    send_message(settings.SERVER_EMAIL, [user.email], subject, rendered)
