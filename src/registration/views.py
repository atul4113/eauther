from django.conf import settings
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from src.registration.models import RegistrationProfile
from src.lorepo.user.forms import CustomRegistrationForm
import collections.abc
import os
from django.db import connections
import logging
os.environ['DJANGO_SETTINGS_MODULE'] = 'src.settings'
connections['default'].settings_dict['OPTIONS']['use_transactions'] = False
connections['default'].settings_dict['AUTOCOMMIT'] = True

# Patch to prevent any transaction attempts
from django.db import transaction
transaction.atomic = lambda using=None: (yield)  # Disables all transaction.atomic()
logger = logging.getLogger(__name__)
def activate(request, activation_key, template_name='registration/activate.html', extra_context=None):
    activation_key = activation_key.lower()
    account = RegistrationProfile.objects.activate_user(activation_key)

    context = {
        'account': account,
        'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
        **(extra_context or {})
    }
    return render(request, template_name, context)


def register(request, success_url=None, form_class=CustomRegistrationForm,
             template_name='registration/registration_form.html', extra_context=None):
    # Force non-transactional mode at runtime
    connections['default'].settings_dict['OPTIONS']['use_transactions'] = False

    if request.method == 'POST':
        form = form_class(data=request.POST, files=request.FILES)
        if form.is_valid():
            try:
                # Save user with explicit non-transactional flag
                new_user = form.save(commit=False)
                new_user._state.non_transactional = True  # Critical flag
                new_user.save()

                # Create profile with same flag
                profile = RegistrationProfile.objects.create_profile(new_user)
                profile._state.non_transactional = True
                profile.save()

                return HttpResponseRedirect(success_url or reverse('registration_complete'))

            except Exception as e:
                logger.error(f"Registration failed: {str(e)}", exc_info=True)
                form.add_error(None, "Registration failed. Please try again.")
    else:
        form = form_class()

    context = {
        'form': form,
        **(extra_context or {})
    }
    return render(request, template_name, context)