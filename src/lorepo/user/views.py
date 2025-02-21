# -*- coding: utf-8 -*-
from django.template.loader import render_to_string
from google.appengine._internal.django.conf.global_settings import AUTHENTICATION_BACKENDS
from django.contrib.auth import load_backend, login
from google.appengine.api.modules import get_current_module_name
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import logout, password_reset
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from registration.views import register as original_register
from lorepo.spaces.models import Space, SpaceAccess, AccessRightType
from django.contrib.auth.models import User
from lorepo.spaces.util import get_spaces_subtree
from lorepo.mycontent.util import get_contents_from_specific_space
from django.contrib.auth.forms import PasswordChangeForm
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from lorepo.filestorage.models import FileStorage
from lorepo.user.forms import CustomRegistrationForm, EmailChangeForm,\
    CustomPasswordResetForm, LanguageChoiceForm
from lorepo.mycontent.models import Content, DefaultTemplate, ContentType, CurrentlyEditing
from remember_me.views import remember_me_login
from libraries.utility.queues import trigger_backend_task
from lorepo.spaces.service import insert_space
from lorepo.mycontent.forms import DefaultTemplateForm
from django.forms.util import ErrorList
import settings
from lorepo.permission.models import Permission, Role
from django.core.mail import mail_admins
from lorepo.course.models import Course
import datetime
from libraries.utility.environment import get_versioned_module
from django.template.context import Context
from django.template import loader
from lorepo.mycontent.service import add_content_to_space
from xml.dom import minidom
import logging
from libraries.utility.decorators import backend
from mauthor.admin.models import AdminLog
from lorepo.mycontent.signals import metadata_updated_async
from lorepo.user.models import UserProfile

def custom_login(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/')
    else:
        return remember_me_login(request)

@login_required
def logout_view(request):
    currently_editing = CurrentlyEditing.objects.filter(user=request.user)
    if len(currently_editing) > 0:
        if request.GET.get('force'):
            currently_editing.delete()
            return logout(request, "/")
        messages.error(request, 'Logout failed!', 'danger')
        return render(request, 'user/confirm_logout.html',{'currently_editing' : currently_editing})
    return logout(request, "/")

def custom_reset_password(request):
    return password_reset(request, password_reset_form = CustomPasswordResetForm, from_email = settings.SERVER_EMAIL)

@csrf_protect
@login_required
def profile_view(request,
                 password_change_form=PasswordChangeForm,
                 email_change_form=EmailChangeForm,
                 language_form = LanguageChoiceForm):

    password_form = password_change_form(user=request.user)
    email_form = email_change_form(user=request.user)
    lang_form = language_form(user=request.user)

    if request.method == "POST":
        if request.POST.get('email') is None and request.POST.get('old_password') is not None: 
            password_form = password_change_form(user=request.user, data=request.POST)
            if password_form.is_valid():
                password_form.save()
                messages.success(request, 'Password changed.')
        elif request.POST.get('email') is not None:
            email_form = email_change_form(user=request.user, data=request.POST)
            if email_form.is_valid():
                email_form.save()
                messages.success(request, 'E-mail changed.')
        elif request.POST.get('language') is not None:
            lang_form = language_form(user=request.user, data=request.POST)
            if lang_form.is_valid():
                lang_form.save()
                messages.success(request, 'Prefered language changed.')

    return render(request, 'user/profile.html',
                  {
                   'password_form'     :       password_form,
                   'email_form'        :       email_form,
                   'lang_form'        :       lang_form,
                  })

def privacy(request):
    return render(request, 'user/privacy.html')

def terms(request):
    return render(request, 'user/terms.html')

@login_required
def settings_view(request):
    return render(request, 'user/settings.html')


def profile_callback(user):
    up = UserProfile(user=user)
    up.save()
    return up


def register(request, success_url=None,
             form_class=CustomRegistrationForm,
             template_name='registration/registration_form.html',
             extra_context=None):
    '''Overrides the original register method.
    Beside creating the user in the usual way it creates a default private space
    for the user and sets the user as an owner.
    '''

    result = original_register(request, success_url, form_class, profile_callback, template_name, extra_context)
    if request.method == 'POST' and result.status_code == 302:
        form = form_class(data=request.POST, files=request.FILES)
        username = form.data['username']
        user = User.objects.get(username__iexact=username)
        space = Space(title=username)
        insert_space(space)
        role = Role(name = 'owner', permissions = Permission().get_all())
        role.save()
        space_access = SpaceAccess(user=user, space=space, roles = [role.pk])
        space_access.save()
    return result

@login_required
@user_passes_test(lambda user: user.is_superuser)
def edit_xml(request):
    if not request.user.is_superuser:
        raise Http404

    if request.method == 'POST':
        fs = FileStorage.objects.get(pk=request.POST.get('id'))
        fs.contents = request.POST.get('contents').encode('utf-8')
        fs.save()
        return HttpResponseRedirect('/user/settings')
    else:
        fs = FileStorage.objects.get(pk=request.GET.get('id'))
        return render(request, 'user/xmleditor.html', {'fs' : fs})

@user_passes_test(lambda user: user.is_superuser)
@login_required
def show_spaces_tree(request, space_id):
    space = Space.objects.get(pk=space_id)
    return render(request, 'user/spaces_tree.html', {'spaces' : [space]})

@backend
def fix_lesson(request, content_id):
    content = Content.get_cached(id=content_id)
    try:
        for space in content.spaces:
            s = Space.objects.get(pk=space)
            if s.is_deleted and not content.is_deleted:
                content.is_deleted = True
                content.save()
                metadata_updated_async.send(sender=None, content_id=content.id)
                log = AdminLog(entity='Content', key=content.id, description='Is deleted -> true if any space in path is deleted')
                log.identifier = 'DELETE_CONTENTS_FROM_DELETED_SPACES'
                log.save()
    except Exception:
        import traceback
        logging.error(traceback.format_exc())
    return HttpResponse("ok")

@backend
def fix(request):
    count = Content.objects.all().count()
    for n in range(0, count/30 + 1):
        logging.error("Current batch: %s", n)
        contents = Content.objects.all()[n*30:(n+1)*30]
        for content in contents:
            if content.is_deleted:
                continue
            trigger_backend_task('/user/fixlesson/%s' % content.id, target=get_versioned_module(get_current_module_name()), queue_name='default')
    mail_admins('Fix done', 'DONE')
    return HttpResponse('OK')


def _fix_courses_id():
    for course in Course.objects.all():
        parsed_xml = minidom.parseString(course.structure_xml.contents)
        parsed_xml.getElementsByTagName('course')[0].setAttribute('id', str(course.id))
        course.save_structure_xml(parsed_xml)

def _fix_roles(sa):
    company = sa.space.top_level
    if sa.access_right == AccessRightType.OWNER:
        name = 'owner'
        permissions = Permission().get_all()
    elif sa.access_right == AccessRightType.READ:
        name = 'read'
        permissions = [
            Permission.CONTENT_VIEW,
            Permission.BUGTRACK_ADD
        ]
    elif sa.access_right == AccessRightType.WRITE:
        name = 'write'
        permissions = [
            Permission.ASSET_BROWSE,
            Permission.ASSET_EDIT,
            Permission.ASSET_REMOVE,
            Permission.BUGTRACK_ADD,
            Permission.CONTENT_SHOW_HISTORY,
            Permission.BACKUP_ADMIN,
            Permission.CONTENT_VIEW,
            Permission.CONTENT_COPY,
            Permission.CONTENT_EDIT,
            Permission.CONTENT_EDIT_HISTORY,
            Permission.CONTENT_EDIT_METADATA,
            Permission.CONTENT_ICON,
            Permission.CONTENT_MAKE_PUBLIC,
            Permission.CONTENT_REMOVE,
            Permission.CONTENT_SHOW_HISTORY,
            Permission.EXCHANGE_EXPORT,
            Permission.EXCHANGE_IMPORT,
            Permission.LOCALIZATION_CREATE,
            Permission.LOCALIZATION_EXPORT,
            Permission.LOCALIZATION_IMPORT,
            Permission.LOCALIZATION_LOCALIZE,
            Permission.LOCALIZATION_RESET,
            Permission.NARRATION_EXPORT,
            Permission.SPACE_EDIT,
            Permission.SPACE_REMOVE,
            Permission.STATE_SET
        ]
    
    if sa.space.is_corporate():
        role, created = Role.objects.get_or_create(name = name, permissions = permissions, company = company)
    else:
        role, created = Role.objects.get_or_create(name = name, permissions = permissions, company__isnull = True)
    role.save()

    sa.roles = [role.pk]
    sa.save()

@backend
def activate(request):
    try:
        count = User.objects.count()
        for n in range(0, count/30 + 1):
            users = User.objects.all()[n*30:(n+1)*30]
            for user in users:
                user.is_active = True
                user.save()
    except Exception:
        pass
    return HttpResponse('OK')

@login_required
@user_passes_test(lambda user: user.is_superuser)
def trigger_task(request):
    trigger_backend_task(request.POST.get('path'), queue_name=request.POST.get('queue'), target=get_versioned_module(request.POST.get('backend')))
    messages.success(request, 'Your request will now run in background')
    return HttpResponseRedirect('/user/settings')

@user_passes_test(lambda user: user.is_superuser)
@login_required
def orphaned_spaces(request, top_level_space):
    top_level = Space.objects.get(pk=top_level_space)
    spaces = Space.objects.filter(top_level=top_level)
    orphaned = []
    for space in spaces:
        try:
            space.parent
        except:
            subspaces = get_spaces_subtree(space.id)
            count = 0
            for s in subspaces:
                contents = get_contents_from_specific_space(s.id)
                count = count + len(contents)
            space.contents = count
            orphaned.append(space)
    return render(request, 'user/orphaned_spaces.html', {'orphaned' : orphaned})

@user_passes_test(lambda user: user.is_superuser)
@login_required
def change_global_template(request):
    form = DefaultTemplateForm()
    current_template = None
    if request.method == 'POST':
        form = DefaultTemplateForm(request.POST)
        if form.is_valid():
            template_id = form.cleaned_data['template_id']
            template = Content.get_cached_or_none(template_id)
            if template and template.content_type == ContentType.TEMPLATE:
                for default_template in DefaultTemplate.objects.all():
                    default_template.delete()
                dt = DefaultTemplate(template=template)
                dt.save()
                messages.success(request, 'Global template changed to %s' % template)
                return HttpResponseRedirect('/user/settings')
            else:
                errors = form._errors.setdefault("template_id", ErrorList())
                errors.append('Template with id %s not found.' % template_id)
    else:
        dts = DefaultTemplate.objects.all()
        dt = dts[0] if len(dts) > 0 else None
        current_template = dt.template if dt else None
    return render(request, 'user/global_template.html', { 'current_template' : current_template, 'form' : form })

@user_passes_test(lambda user: user.is_superuser)
@login_required
def remove_global_template(request):
    for default_template in DefaultTemplate.objects.all():
        default_template.delete()
    messages.success(request, 'Global template set to none.')
    return HttpResponseRedirect('/user/settings')

@backend
def update_owners_permissions(request):
    roles = Role.objects.filter(name = 'owner')
    for role in roles:
        try:
            role.permissions = Permission().get_all()
            role.save()
        except Exception:
            import traceback
            mail_admins('Update owners permissions error', traceback.format_exc())
    mail_admins('Update owners permissions done', '%s' % len(roles))
    return HttpResponse()

@backend
def create_lessons(request, user_id, space_id, count):
    user = User.objects.get(pk = user_id)
    space = Space.objects.get(pk = space_id)

    for i in range(0, int(count)):
        now = datetime.datetime.now()

        t = render_to_string('initdata/lesson/page.xml', {}).encode('utf-8')
        pageFile = FileStorage(
                       created_date = now,
                       modified_date = now,
                       content_type = "text/xml",
                       contents = t,
                       owner = user
                   )
        pageFile.save()
        
        # Add empty content file
        params = {'page' : pageFile }

        t = render_to_string('initdata/lesson/content.xml', params).encode('utf-8')

        contentFile = FileStorage(
                           created_date = now,
                           modified_date = now,
                           content_type = "text/xml",
                           contents = t,
                           owner = user
                       )
        contentFile.version = 1
        contentFile.save()
        
        # Register content in database
        content = Content(
                    title = 'Sample Lesson %s' % i,
                    tags = '',
                    description = '', 
                    short_description = '',
                    created_date = now, 
                    modified_date = now, 
                    author = user,
                    file = contentFile
                )
        
        content.add_title_to_xml()
        content.save()
        contentFile.history_for = content
        contentFile.save()
        
        add_content_to_space(content, space)
    return HttpResponse()

def login_as(request, user_id):
    user = get_object_or_404(User, pk = user_id)
    if not hasattr(user, 'backend'):
        for backend in AUTHENTICATION_BACKENDS:
            if user == load_backend(backend).get_user(user.pk):
                user.backend = backend
                break
    login(request, user)
    return redirect("/")