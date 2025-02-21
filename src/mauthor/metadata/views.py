from django.utils.translation import get_language_info
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import mail_admins
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.template.context import Context
from django.template import loader
from libraries.utility.decorators import backend
from libraries.utility.environment import get_versioned_module
from libraries.utility.queues import trigger_backend_task
from lorepo.public.util import send_message
from lorepo.spaces.models import Space
from mauthor.utility.decorators import company_admin
from mauthor.metadata.models import Definition, MetadataValue
import logging
from mauthor.metadata.util import get_metadata_definitions
from django.views.decorators.http import require_POST

@login_required
@company_admin
def define(request):
    try:
        language_bidi = get_language_info(request.user.language_code_bidi)['bidi']
    except KeyError: #for some unknown reason on ocassion language_code_bidi is none
        language_bidi = False
    definitions = get_metadata_definitions(request.user.company)
    return render(request, 'metadata/define.html', {'definitions' : definitions,
                                                    'language_bidi': language_bidi})

@login_required
@company_admin
@require_POST
def store(request):
    Definition.objects.filter(company=request.user.company).delete()
    types = request.POST.getlist('type')
    names = request.POST.getlist('name')
    descriptions = request.POST.getlist('description')
    values = request.POST.getlist('values')
    for counter, current_type in enumerate(types):
        definition = Definition(company=request.user.company,
                                field_type=current_type,
                                name=names[counter],
                                description=descriptions[counter],
                                value=values[counter],
                                order=counter)
        definition.save()
    if 'batch_update' in request.POST:
        messages.success(request, "Your lessons will be updated, you will receive an email upon completion.")
        trigger_backend_task('/metadata/batch_update/%s/%s'%(request.user.company.id, request.user.id), target=get_versioned_module('download'), queue_name='default')
    else:
        messages.success(request, "Definitions successfully saved")
    return HttpResponseRedirect('/corporate/admin')

@backend
def batch_update(request, company_id, user_id):
    '''
        Remove all extended metadata values from lessons and lesson pages
        that do not have a matching extended metadata definition.
    '''
    try:
        company = get_object_or_404(Space, pk = company_id)
        user = get_object_or_404(User, pk=user_id)
        defs = Definition.objects.filter(company=company)
        names = [definition.name for definition in defs]
        metavalues_queryset =  MetadataValue.objects.filter(company=company)
        metavalues_count = metavalues_queryset.count()
        for offset in range(0,metavalues_count, 500):
            querysubset = metavalues_queryset[offset:offset+500]
            for metavalue in querysubset:
                if metavalue.name not in names:
                    metavalue.delete()
        send_success_confirmation(company, user, 'assets/metadata_batch_success.txt')
    except Exception:
        import traceback
        logging.error("Error while importing assets package: %s", traceback.format_exc())
        mail_admins('Batch update of extended metadata failed.', traceback.format_exc())
        send_failure_confirmation(company, user, 'assets/metadata_batch_failure.txt')

    return HttpResponse("OK")


def send_failure_confirmation(company, user, template):
    subject = 'Batch update for company "%s" has failed' % company.title
    context = Context({'company': company, 'user': user, 'settings': settings})
    email = loader.get_template(template)
    rendered = email.render(context)
    send_message(settings.SERVER_EMAIL, [user.email], subject, rendered)


def send_success_confirmation(company, user, template):
    subject = 'Batch update for company "%s" is complete' % company.title
    context = Context({'company': company, 'user': user, 'settings': settings})
    email = loader.get_template(template)
    rendered = email.render(context)
    send_message(settings.SERVER_EMAIL, [user.email], subject, rendered)
