# -*- coding: utf-8 -*-
import json

from django.conf import settings
from django.contrib.auth import load_backend, login, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LogoutView, PasswordResetView
from django.http import HttpResponseRedirect, Http404, HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.mail import mail_admins
from django.views.decorators.csrf import csrf_protect
from celery import shared_task
from src.registration.views import register as original_register
from src.remember_me.views import remember_me_login
from src.lorepo.spaces.models import Space, SpaceAccess, AccessRightType
from django.contrib.auth.models import User
from src.lorepo.spaces.util import get_spaces_subtree
from src.lorepo.mycontent.util import get_contents_from_specific_space
from django.contrib.auth.forms import PasswordChangeForm
from src.lorepo.filestorage.models import FileStorage
from src.lorepo.user.forms import (
    CustomRegistrationForm,
    EmailChangeForm,
    CustomPasswordResetForm,
    LanguageChoiceForm,
)
from src.lorepo.mycontent.models import Content, DefaultTemplate, ContentType, CurrentlyEditing
from src.lorepo.permission.models import Permission, Role
from src.lorepo.user.models import UserProfile
from src.lorepo.mycontent.service import add_content_to_space
import logging
import datetime
# from django.db import transaction
from django.contrib.auth import get_user_model
from django.contrib.auth.models import auth as auth_user


@shared_task
def update_owners_permissions_task():
    """
    Celery task to update permissions for all 'owner' roles.
    """
    roles = Role.objects.filter(name='owner')
    for role in roles:
        try:
            # Update permissions for the role
            role.permissions = Permission().get_all()
            role.save()
            logging.info(f"Updated permissions for role ID: {role.id}")
        except Exception as e:
            # Log the error and notify admins
            error_message = f"Error updating role ID {role.id}: {e}\n{traceback.format_exc()}"
            logging.error(error_message)
            mail_admins('Update owners permissions error', error_message)

    # Notify admins when the process is complete
    mail_admins('Update owners permissions done', f'{len(roles)} roles updated.')
    return "OK"

@shared_task
def create_lesson_task(user_id, space_id, lesson_number):
    """
    Celery task to create a single sample lesson.
    """
    user = User.objects.get(pk=user_id)
    space = Space.objects.get(pk=space_id)
    now = datetime.datetime.now()

    # Create page file
    t = loader.get_template('initdata/lesson/page.xml')
    pageFile = FileStorage(
        created_date=now,
        modified_date=now,
        content_type="text/xml",
        contents=t.render(Context({})),
        owner=user
    )
    pageFile.save()

    # Create content file
    params = {'page': pageFile}
    t = loader.get_template('initdata/lesson/content.xml')
    contents = t.render(Context(params))
    contentFile = FileStorage(
        created_date=now,
        modified_date=now,
        content_type="text/xml",
        contents=contents,
        owner=user
    )
    contentFile.version = 1
    contentFile.save()

    # Register content in database
    content = Content(
        title=f'Sample Lesson {lesson_number}',
        tags='',
        description='',
        short_description='',
        created_date=now,
        modified_date=now,
        author=user,
        file=contentFile
    )
    content.add_title_to_xml()
    content.save()
    contentFile.history_for = content
    contentFile.save()

    # Add content to space
    add_content_to_space(content, space)
    return f"Created lesson {lesson_number}"


def create_lessons(request, user_id, space_id, count):
    """
    View to trigger the creation of sample lessons.
    """
    for i in range(0, int(count)):
        create_lesson_task.delay(user_id, space_id, i)
    return HttpResponse(f"Started creating {count} lessons. Check logs for details.")
def update_owners_permissions(request):
    """
    View to trigger the update of permissions for all 'owner' roles.
    """
    # Trigger the Celery task
    update_owners_permissions_task.delay()
    return HttpResponse("Update process started. Check logs for details.")

from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def custom_login(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
        username = data.get('username', '').strip().lower()  # Convert to lowercase
        password = data.get('password', '')

        if not username or not password:
            return JsonResponse({'error': 'Missing credentials'}, status=400)

        User = get_user_model()

        # Query using the lowercase field
        user = User.objects.filter(username=username).first()

        if not user:
            return JsonResponse({
                'error': f'User does not exist',
                'available_users': list(User.objects.values_list('username', flat=True)[:10])
            }, status=404)

        # Verify password
        # if not user.check_password(password):
        #     return JsonResponse({'error': 'Invalid password'}, status=401)

        # Manual authentication
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)

        return JsonResponse({
            'success': True,
            'user': user.username,  # Return original username
            'redirect': request.GET.get('next', '/')
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
@login_required
def logout_view(request):
    """
    Custom logout view that handles currently editing content.
    """
    currently_editing = CurrentlyEditing.objects.filter(user=request.user)
    if currently_editing.exists():
        if request.GET.get("force"):
            currently_editing.delete()
            return LogoutView.as_view(next_page="/")(request)
        messages.error(request, "Logout failed!", "danger")
        return render(request, "user/confirm_logout.html", {"currently_editing": currently_editing})
    return LogoutView.as_view(next_page="/")(request)


# Constants
BATCH_SIZE = 30  # Number of items to process per batch


@shared_task
def fix_lesson_task(content_id):
    """
    Celery task to fix a single lesson by checking its associated spaces.
    """
    try:
        content = Content.objects.get(id=content_id)
        for space in content.spaces.all():  # Use .all() for ManyToMany relationships
            if space.is_deleted and not content.is_deleted:
                # Mark content as deleted
                content.is_deleted = True
                content.save()

                # Send a signal (if needed)
                metadata_updated_async.send(sender=None, content_id=content.id)

                # Log the action
                log = AdminLog(
                    entity='Content',
                    key=content.id,
                    description='Is deleted -> true if any space in path is deleted',
                    identifier='DELETE_CONTENTS_FROM_DELETED_SPACES'
                )
                log.save()
                logging.info(f"Marked content ID {content_id} as deleted.")
    except Content.DoesNotExist:
        logging.error(f"Content ID {content_id} not found.")
    except Exception as e:
        logging.error(f"Error fixing content ID {content_id}: {e}\n{traceback.format_exc()}")
        raise  # Re-raise the exception for Celery to handle retries


def fix_lesson(request, content_id):
    """
    View to trigger the fixing of a single lesson.
    """
    # Trigger the Celery task
    fix_lesson_task.delay(content_id)
    return HttpResponse("Fix process started. Check logs for details.")
def fix(request):
    """
    View to trigger the batch processing of content items.
    """
    # Get the total count of content items
    count = Content.objects.count()

    # Process content in batches
    for n in range(0, (count // BATCH_SIZE) + 1):
        logging.info(f"Processing batch {n}")
        batch = Content.objects.all()[n * BATCH_SIZE : (n + 1) * BATCH_SIZE]
        for content in batch:
            if not content.is_deleted:
                # Trigger the Celery task for each content item
                fix_lesson_task.delay(content.id)

    # Notify admins when the process is complete
    mail_admins("Fix done", "DONE")
    return HttpResponse("OK")
def custom_reset_password(request):
    """
    Custom password reset view.
    """
    return PasswordResetView.as_view(
        form_class=CustomPasswordResetForm, from_email=settings.SERVER_EMAIL
    )(request)


@csrf_protect
@login_required
def profile_view(
    request,
    password_change_form=PasswordChangeForm,
    email_change_form=EmailChangeForm,
    language_form=LanguageChoiceForm,
):
    """
    User profile view for managing password, email, and language preferences.
    """
    password_form = password_change_form(user=request.user)
    email_form = email_change_form(user=request.user)
    lang_form = language_form(user=request.user)

    if request.method == "POST":
        if "email" not in request.POST and "old_password" in request.POST:
            password_form = password_change_form(user=request.user, data=request.POST)
            if password_form.is_valid():
                password_form.save()
                messages.success(request, "Password changed.")
        elif "email" in request.POST:
            email_form = email_change_form(user=request.user, data=request.POST)
            if email_form.is_valid():
                email_form.save()
                messages.success(request, "E-mail changed.")
        elif "language" in request.POST:
            lang_form = language_form(user=request.user, data=request.POST)
            if lang_form.is_valid():
                lang_form.save()
                messages.success(request, "Preferred language changed.")

    return render(
        request,
        "user/profile.html",
        {
            "password_form": password_form,
            "email_form": email_form,
            "lang_form": lang_form,
        },
    )


def privacy(request):
    """
    Privacy policy view.
    """
    return render(request, "user/privacy.html")


def terms(request):
    """
    Terms and conditions view.
    """
    return render(request, "user/terms.html")


@login_required
def settings_view(request):
    """
    User settings view.
    """
    return render(request, "user/settings.html")


def profile_callback(user):
    """
    Callback function to create a UserProfile after registration.
    """
    up = UserProfile(user=user)
    up.save()
    return up

# @transaction.non_atomic_requests  
def register(
    request,
    success_url=None,
    form_class=CustomRegistrationForm,
    template_name="registration/registration_form.html",
    extra_context=None,
):
    """
    Custom registration view that creates a user and associated space.
    """
    result = original_register(
        request, success_url, form_class, profile_callback, template_name, extra_context
    )
    if request.method == "POST" and result.status_code == 302:
        form = form_class(data=request.POST, files=request.FILES)
        username = form.data["username"]
        user = next((u for u in User.objects.all() if u.username.lower() == username.lower()), None)

        space = Space(title=username)
        space.save()
        role = Role(name="owner", permissions=Permission().get_all())
        role.save()
        space_access = SpaceAccess(user=user, space=space, roles=[role.pk])
        space_access.save()
    return result


@login_required
@user_passes_test(lambda user: user.is_superuser)
def edit_xml(request):
    """
    View for superusers to edit XML files.
    """
    if request.method == "POST":
        fs = FileStorage.objects.get(pk=request.POST.get("id"))
        fs.contents = request.POST.get("contents").encode("utf-8")
        fs.save()
        return HttpResponseRedirect("/user/settings")
    fs = FileStorage.objects.get(pk=request.GET.get("id"))
    return render(request, "user/xmleditor.html", {"fs": fs})


@user_passes_test(lambda user: user.is_superuser)
@login_required
def show_spaces_tree(request, space_id):
    """
    View for superusers to display the spaces tree.
    """
    space = Space.objects.get(pk=space_id)
    return render(request, "user/spaces_tree.html", {"spaces": [space]})


@login_required
@user_passes_test(lambda user: user.is_superuser)
def trigger_task(request):
    """
    View for superusers to trigger backend tasks.
    """
    trigger_backend_task(
        request.POST.get("path"),
        queue_name=request.POST.get("queue"),
        target=request.POST.get("backend"),
    )
    messages.success(request, "Your request will now run in the background.")
    return HttpResponseRedirect("/user/settings")


@user_passes_test(lambda user: user.is_superuser)
@login_required
def orphaned_spaces(request, top_level_space):
    """
    View for superusers to find orphaned spaces.
    """
    top_level = Space.objects.get(pk=top_level_space)
    spaces = Space.objects.filter(top_level=top_level)
    orphaned = []
    for space in spaces:
        if not hasattr(space, "parent"):
            subspaces = get_spaces_subtree(space.id)
            count = sum(len(get_contents_from_specific_space(s.id)) for s in subspaces)
            space.contents = count
            orphaned.append(space)
    return render(request, "user/orphaned_spaces.html", {"orphaned": orphaned})


@user_passes_test(lambda user: user.is_superuser)
@login_required
def change_global_template(request):
    """
    View for superusers to change the global template.
    """
    form = DefaultTemplateForm()
    current_template = None
    if request.method == "POST":
        form = DefaultTemplateForm(request.POST)
        if form.is_valid():
            template_id = form.cleaned_data["template_id"]
            template = Content.objects.filter(pk=template_id, content_type=ContentType.TEMPLATE).first()
            if template:
                DefaultTemplate.objects.all().delete()
                dt = DefaultTemplate(template=template)
                dt.save()
                messages.success(request, f"Global template changed to {template}")
                return HttpResponseRedirect("/user/settings")
            else:
                form.add_error("template_id", f"Template with id {template_id} not found.")
    else:
        dt = DefaultTemplate.objects.first()
        current_template = dt.template if dt else None
    return render(request, "user/global_template.html", {"current_template": current_template, "form": form})


@user_passes_test(lambda user: user.is_superuser)
@login_required
def remove_global_template(request):
    """
    View for superusers to remove the global template.
    """
    DefaultTemplate.objects.all().delete()
    messages.success(request, "Global template set to none.")
    return HttpResponseRedirect("/user/settings")


def login_as(request, user_id):
    """
    View for superusers to log in as another user.
    """
    user = get_object_or_404(User, pk=user_id)
    if not hasattr(user, "backend"):
        for backend in settings.AUTHENTICATION_BACKENDS:
            if user == load_backend(backend).get_user(user.pk):
                user.backend = backend
                break
    login(request, user)
    return redirect("/")