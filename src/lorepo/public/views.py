from src.lorepo.public.forms import ContactForm, OrderForm
from src.lorepo.filestorage.views import get_file
from django.template import loader

from django.shortcuts import render, get_object_or_404
from src.lorepo.mycontent.util import get_content_details
from src.lorepo.mycontent.models import ContentType, Content
from src.lorepo.spaces.util import get_spaces_for_copy, get_private_space_for_user
from django.http import Http404, HttpResponseRedirect
from django.template.context import Context
from src.lorepo.public.util import send_message
from src import settings

def view(request, content_id):
    return HttpResponseRedirect('/embed/%s' % content_id)

def view_addon(request, addon_id):
    context = get_content_details(request, addon_id, ContentType.ADDON)
    
    if not context['content'].is_content_public() and not request.user.is_superuser:
        raise Http404

    if request.user.is_authenticated():
        context['copy_spaces'] = get_spaces_for_copy(request.user)
        context['private_space'] = get_private_space_for_user(request.user)
    else:
        context['copy_spaces'] = []
    
    context['is_public'] = True
    context['spaces'] = context['public_spaces'] 
    context['addon'] = context['content']
    context['related'] = context['related_presentations']
    return render(request, 'public/view_addon.html', context)


def get_addon(request, addon_id):
    '''Serve the addon to the editor
    '''
    addon = get_object_or_404(Content, name=addon_id)
    if addon.public_version is None:
        raise Http404
    return get_file(request, addon.public_version.id)

def full(request, content_id):
    return HttpResponseRedirect('/embed/full/' + content_id)


def order_account(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            data = Context(form.cleaned_data)
            email = loader.get_template('emails/order_account.txt')
            send_message(settings.SERVER_EMAIL, [settings.LEARNETIC_EMAIL], "Account order - %s" % settings.APP_NAME,
                         email.render(data))
            return render(request, 'public/order-account-thanks.html')
    else:
        try:
            users = request.GET['users']
        except Exception as e:
            users = None
        form = OrderForm()
        form.set_users(users)

    return render(request, 'public/order-account.html', {'form': form})


def contact_us(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            data = Context(form.cleaned_data)
            email = loader.get_template('emails/contact_us.txt')
            send_message(settings.SERVER_EMAIL, [settings.LEARNETIC_EMAIL], "Message from %s contact form" % settings.APP_NAME, email.render(data))
            return render(request, 'public/contact-us-thanks.html')
    else:
        form = ContactForm()

    return render(request, 'public/contact-us.html', {'form': form})


def player(request):
    return render(request, 'public/player.html')


def learn_more(request):
    return render(request, 'public/learn-more.html')


def samples(request):
    return render(request, 'public/samples.html')


def content_mp(request):
    return render(request, 'public/content_mp.html')


def developers_mp(request):
    return render(request, 'public/developers_mp.html')


def pricing_plans(request):
    return render(request, 'public/pricing_plans.html')


def login_register_info(request):
    return render(request, 'public/login_register_info.html')
