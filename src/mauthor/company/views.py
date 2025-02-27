from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404
from src.libraries.utility.helpers import get_object_or_none
from src.lorepo.corporate.models import CompanyUser
from src.lorepo.permission.models import Role
from src.lorepo.spaces.util import  get_spaces_tree
from src.lorepo.spaces.models import Space, SpaceAccess, LockedSpaceAccess, SpaceType
from src.mauthor.utility.decorators import company_admin
from src.mauthor.company.util import get_company_properties, get_users_from_company, invalidate_language_cache_for_company_users
from src.mauthor.company.forms import EditCompanyForm
from django.http import HttpResponseRedirect
from django.contrib import messages
from src.libraries.utility.cacheproxy import delete_template_fragment_cache
from src.lorepo.corporate.signals import company_structure_changed
from src.lorepo.mycontent.models import Content
from django.contrib.auth.models import User

COMPANY_LANGUAGES = [('en', 'Left to Right'),
                     ('ar', 'Right to Left')]

@user_passes_test(lambda user: user.is_superuser)
@login_required
def companies_report(request):
    all_companies = Space.objects.filter(space_type=SpaceType.CORPORATE, parent=None, is_deleted=False).order_by('title')

    for space in all_companies:
        if LockedSpaceAccess.objects.filter(space = space).count() > 0:
            space.is_blocked = True
        space.users_count = CompanyUser.objects.filter(company = space).count()
        space.properties = get_company_properties(space)
        if space.properties.max_accounts and space.users_count > space.properties.max_accounts:
            space.user_limit_exceeded = True

    companies = [x for x in all_companies if x.is_test is False or x.is_test is None]
    test_companies = [x for x in all_companies if x.is_test is True]

    return render(request, 'company/report_companies.html', {
        'spaces' : companies,
        'test_companies' : test_companies})


@user_passes_test(lambda user: user.is_superuser)
@login_required
def remove_company_from_test(request):
    test_space = get_object_or_404(Space, pk=request.POST.get("space_id"))
    test_space.is_test = False
    test_space.save()
    return HttpResponseRedirect('/company/list_companies')


@company_admin
@login_required
def details(request, space_id):
    company = get_object_or_404(Space, pk=space_id)
    properties = get_company_properties(company)
    company_users = get_users_from_company(company)
    count = Content.objects.filter(spaces = space_id, is_deleted=False).count()

    for company_user in company_users:
        company_user.roles = []
        user_object = get_object_or_none(User, username=company_user.username)
        if user_object is not None:
            access = get_object_or_none(SpaceAccess, user=user_object, space=company)

            if access is not None:
                for role_id in access.roles:
                    role = get_object_or_none(Role, id=role_id)
                    if role is not None:
                        company_user.roles.append(role.name)

    return render(request, 'company/details.html', {
                                    'company' : company,
                                    'properties' : properties,
                                    'users' : company_users,
                                    'contents' : count})

@company_admin
@login_required
def edit_details(request, space_id):
    company = get_object_or_404(Space, pk=space_id)
    properties = get_company_properties(company)
    if request.POST:
        form = EditCompanyForm(request.POST)
        if form.is_valid():
            company.title = form.cleaned_data['space']
            company.save()
            properties.max_accounts = form.cleaned_data['max_accounts']
            properties.valid_until = form.cleaned_data['valid_until']
            if properties.language_code != request.POST['language']:
                properties.language_code = request.POST['language']
                properties.save()
                invalidate_language_cache_for_company_users(company)
            else:
                properties.save()
            messages.info(request, 'Company details saved')
            return HttpResponseRedirect('/company/details/' + str(company.id))
    else:
        form = EditCompanyForm({'space' : company.title,
                                'max_accounts' : properties.max_accounts,
                                'valid_until' : properties.valid_until
                                })
    return render(request, 'company/edit.html', {
                                    'company' : company,
                                    'properties' : properties,
                                    'languages' : COMPANY_LANGUAGES,
                                    'form' : form
                                                 })


@company_admin
@login_required
def edit_locale(request, space_id):
    company = get_object_or_404(Space, pk=space_id)
    properties = get_company_properties(company)
    if request.POST:
        selected_lang = request.POST['language']
        lang_codes = [code for code, name in COMPANY_LANGUAGES]
        if properties.language_code != selected_lang and selected_lang in lang_codes:
            properties.language_code = selected_lang
            properties.save()
            invalidate_language_cache_for_company_users(company)
            messages.info(request, 'Company locale saved')
            properties.save()
            return HttpResponseRedirect('/corporate/admin')
    return render(request, 'company/edit_locale.html', {
                                    'company' : company,
                                    'properties' : properties,
                                    'languages' : COMPANY_LANGUAGES
                                    })


@company_admin 
@login_required
def lock(request, space_id):
    company_spaces = list( get_spaces_tree(space_id) )
    space_accesses = []
    for cs in company_spaces:
        space_accesses.extend( SpaceAccess.objects.filter(space = cs) )
    for sa in space_accesses:
        lsa = sa.lock()
        lsa.save()
        sa.delete()
    if len(space_accesses):
        company_structure_changed.send(None, company_id=space_id, user_id = None)
    
    messages.info(request, 'Company <%(company)s> has been locked' % { 'company' : company_spaces[0].top_level })
    delete_template_fragment_cache('menu', request.user)
    return HttpResponseRedirect('/company/list_companies')

@company_admin 
@login_required
def unlock(request, space_id):
    company_spaces = list( get_spaces_tree(space_id) )
    lsas = []
    for cs in company_spaces:
        lsas.extend( LockedSpaceAccess.objects.filter(space = cs) )
    for lsa in lsas:
        sa = lsa.unlock()
        sa.save()
        lsa.delete()
    if len(lsas):
        company_structure_changed.send(None, company_id=space_id, user_id=0)
    
    messages.info(request, 'Company <%(company)s> has been unlocked' % { 'company' : company_spaces[0].top_level })
    delete_template_fragment_cache('menu', request.user)
    return HttpResponseRedirect('/company/list_companies')