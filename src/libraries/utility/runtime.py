from django.http import HttpResponseForbidden
from google.appengine.api.backends import get_backend

def run_on_backend(fn):
    def wrapped(*args, **kwargs):
        backend = get_backend()
        if backend is not None:
            return fn(*args, **kwargs)
        else:
            return HttpResponseForbidden("Forbidden")
    return wrapped