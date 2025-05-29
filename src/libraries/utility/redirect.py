from django.http import HttpResponseRedirect

def get_redirect_url(request, target = '/mycontent'):
    """
    Get the redirect URL from either GET or POST parameters.
    In Django 4.1+, we need to check GET and POST separately as REQUEST is removed.
    """
    # First check GET, then POST, fallback to target if neither has 'next'
    redirect_url = request.GET.get("next") or request.POST.get("next") or target
    return redirect_url

def get_redirect_urls(request, target = '/mycontent'):
    """
    Get multiple redirect URLs from either GET or POST parameters.
    In Django 4.1+, we need to check GET and POST separately as REQUEST is removed.
    """
    # First check GET, then POST, fallback to target if neither has 'next'
    redirect_urls = request.GET.getlist('next') or request.POST.getlist('next') or [target]
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
    """
    Get the redirect URL and return a HttpResponseRedirect.
    In Django 4.1+, we need to check GET and POST separately as REQUEST is removed.
    """
    # First check GET, then POST, fallback to target if neither has 'next'
    target = request.GET.get('next') or request.POST.get('next') or target
    return HttpResponseRedirect(target)