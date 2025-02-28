from django.shortcuts import render, get_object_or_404
from src import settings
from src.libraries.mobile.mobile_utils import is_mobile_user_agent, is_ios_user_agent
from src.lorepo.mycontent.models import Content
from src.lorepo.embed.decorators import check_is_public
from src.lorepo.filestorage.models import FileStorage
from src.lorepo.public.metaseo import MetaSEO
from src.lorepo.spaces.util import is_company_locked
from django.core.exceptions import PermissionDenied


def _check_if_company_locked(request):
    if is_company_locked(request.user.company):
        raise PermissionDenied


@check_is_public
def mobile(request, content_id, version=None):
    if version is not None:
        get_object_or_404(FileStorage, pk=version)
    if is_ios_user_agent(request):
        template = 'embed/mobile_ios.html'
    else:
        template = 'embed/mobile.html'
    return _handle(request, content_id, template, version)

@check_is_public
def editor(request, content_id, version=None):
    if version is not None:
        get_object_or_404(FileStorage, pk=version)
    template = 'embed/editor.html'
    return _handle(request, content_id, template, version)

@check_is_public
def book(request, content_id):
    return _handle(request, content_id, 'embed/book.html')

@check_is_public
def corporate_embed(request, content_id):
    return _handle(request, content_id, 'embed/corporate.html')


@check_is_public
def present(request, content_id):
    content = Content.get_cached_or_404(id=content_id)

    context = {
        'content': content,
        'meta_seo': MetaSEO(request,
                            title='%s - %s' % (content.title, settings.APP_NAME),
                            description=content.short_description,
                            image=content.icon_href)
    }

    if is_ios_user_agent(request):
        return render(request, 'embed/present_mobile_ios.html', context)
    elif is_mobile_user_agent(request):
        return render(request, 'embed/present_mobile.html', context)
    else:
        return render(request, 'embed/present.html', context)


@check_is_public
def iframe(request, content_id):
    return _handle(request, content_id, 'embed/iframe.html')


def _handle(request, content_id, template, version=None):
    _check_if_company_locked(request)
    cover = request.GET.get('cover', False)
    content = Content.get_cached_or_404(id=content_id)
    return render(request, template, {'content': content, 'cover': cover, 'version': version})
