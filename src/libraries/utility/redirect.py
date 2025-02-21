from django.http import HttpResponseRedirect
def get_redirect_url(request, target = '/mycontent'):
    redirect_url = request.REQUEST.get("next") if "next" in request.REQUEST else target
    return redirect_url

def get_redirect_urls(request, target = '/mycontent'):
    redirect_urls = request.REQUEST.getlist('next') if 'next' in request.REQUEST else [target]
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
    if 'next' in request.REQUEST:
        target = request.REQUEST['next']
    return HttpResponseRedirect(target)