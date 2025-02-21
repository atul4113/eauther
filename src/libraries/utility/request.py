
def get_request_value(request, key, default=None):
    if key in request.GET:
        default = request.GET.get(key)
    elif key in request.POST:
        default = request.POST.get(key)
    elif key in request.session:
        default = request.session.get(key)
    request.session[key] = default
    return default

def get_protocol(request):
    if request.META.get('HTTPS') == 'on':
        return 'https'
    return 'http'
