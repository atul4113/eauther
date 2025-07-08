from django.http import HttpResponse, Http404
import logging

def log(request, app_id=None, level=None):
    if not request.user.is_authenticated():
        raise Http404
    params = str(dict(request.GET.items()) | dict(request.POST.items()))
    msg = "[%s] - %s" % (app_id, params)
    logging.log(level, msg)
    return HttpResponse('OK')