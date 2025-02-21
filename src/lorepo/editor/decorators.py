from django.http import HttpResponseForbidden

def is_logged(function):
    def _wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated():
            return HttpResponseForbidden('You are logged out')
        return function(request, *args, **kwargs)
    return _wrapper