from django.conf import settings
from django.urls import reverse  # ✅ Updated import
from django.http import HttpResponseRedirect
from django.shortcuts import render
from src.registration.models import RegistrationProfile
from src.lorepo.user.forms import CustomRegistrationForm
import collections.abc  # ✅ Updated for Callable

def activate(request, activation_key, template_name='registration/activate.html', extra_context=None):
    activation_key = activation_key.lower()  # Normalize before using it.
    account = RegistrationProfile.objects.activate_user(activation_key)

    if extra_context is None:
        extra_context = {}

    # Ensure extra_context values are evaluated if callable
    context = {
        'account': account,
        'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
        **{key: value() if isinstance(value, collections.abc.Callable) else value for key, value in extra_context.items()}
    }

    return render(request, template_name, context)  # ✅ Used render instead of render_to_response

def register(request, success_url=None, form_class=CustomRegistrationForm, profile_callback=None,
             template_name='registration/registration_form.html', extra_context=None):

    if request.method == 'POST':
        print("hey you are in register page 29")
        form = form_class(data=request.POST, files=request.FILES)
        if form.is_valid():
            new_user = form.save(profile_callback=profile_callback)
            return HttpResponseRedirect(success_url or reverse('registration_complete'))
    else:
        form = form_class()

    if extra_context is None:
        extra_context = {}

    context = {
        'form': form,
        **{key: value() if isinstance(value, collections.abc.Callable) else value for key, value in extra_context.items()}
    }

    return render(request, template_name, context)  # ✅ Used render
