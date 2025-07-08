from django.http import HttpResponseRedirect
def get_redirect_url(request, target = '/mycontent'):
    redirect_url = (
        request.GET.get("next") or request.POST.get("next")
        if ("next" in request.GET or "next" in request.POST) else target
    )
    return redirect_url

def get_redirect_urls(request, target = '/mycontent'):
    redirect_urls = (
        request.GET.getlist('next') if 'next' in request.GET else (
            request.POST.getlist('next') if 'next' in request.POST else [target]
        )
    )
    return redirect_urls

def join_redirect_urls(redirect_urls):
    url = ''
    for index, redirect_url in enumerate(redirect_urls):
        if index == 0:
            url = redirect_url
        elif index == 1:
            url = '%s?next=%s' % (url, redirect_url)
        else:
            url = '%s&next=%s' % (url, redirect_url)
    return url

def get_redirect(request, target = '/mycontent'):
    if 'next' in request.GET or 'next' in request.POST:
        target = request.GET.get('next') or request.POST.get('next')
    return HttpResponseRedirect(target)