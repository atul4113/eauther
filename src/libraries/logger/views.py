from django.http import HttpResponse, Http404
import logging

def log(request, app_id=None, level=None):
    if not request.user.is_authenticated():
        raise Http404
    params = str(request.REQUEST)
    msg = "[%s] - %s" % (app_id, params)
    logging.log(level, msg)
    return HttpResponse('OK')