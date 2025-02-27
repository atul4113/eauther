import requests
from django.http import HttpResponse
from django.views.generic import TemplateView
from src.libraries.utility.decorators import localhost_required
from django.utils.decorators import method_decorator


class BasedViewRedirect(TemplateView):

    @method_decorator(localhost_required)
    def get(self, request, *args, **kwargs):
        return self.logic("GET", request.get_full_path(), "")

    @method_decorator(localhost_required)
    def post(self, request, *args, **kwargs):
        return self.logic("POST", request.get_full_path(), request.raw_post_data)

    def logic(self, method, path, payload):
        url = "http://localhost:8002%s" % path

        try:
            # Use the requests library to send the HTTP request
            response = requests.request(method, url, data=payload)
        except requests.RequestException as err:
            response = None

        if response is None:
            return HttpResponse("OK", status=500)
        else:
            return HttpResponse("OK", status=response.status_code)
