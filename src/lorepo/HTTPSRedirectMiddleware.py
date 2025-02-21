from google.appengine.api.modules import get_current_module_name
from django.conf import settings
from django.http import HttpResponsePermanentRedirect
import re

"""
Django SSL (HTTPS) redirection middleware.
Source: https://djangosnippets.org/snippets/880/
"""


class HTTPSRedirect:
    def __init__(self):
        pass

    https_redirect = settings.HTTPS_REDIRECT
    forbidden_urls = (
        r'^/_ah/',
    )

    def process_request(self, request):

        if not self.https_redirect:
            return

        if self._is_secure(request):
            return

        if request.method != "GET":
            return

        if not get_current_module_name() == 'default':
            return

        if request.META.get('HTTP_X_APPENGINE_CRON') is not None:
            return

        urls = tuple([re.compile(url) for url in self.forbidden_urls])
        for url in urls:
            if url.match(request.path):
                return

        return self._redirect(request)

    def _is_secure(self, request):
        if request.is_secure():
            return True

        # Handle the Webfaction case until this gets resolved in the request.is_secure()
        if 'HTTP_X_FORWARDED_SSL' in request.META:
            return request.META['HTTP_X_FORWARDED_SSL'] == 'on'

        return False

    def _redirect(self, request):
        host = getattr(settings, 'SSL_HOST', request.get_host())
        new_url = "https://%s%s" % (host,request.get_full_path())
        if settings.DEBUG and request.method == 'POST':
            raise RuntimeError("""Django can't perform a SSL redirect while maintaining POST data.
           Please structure your views so that redirects only occur during GETs.""")

        return HttpResponsePermanentRedirect(new_url)