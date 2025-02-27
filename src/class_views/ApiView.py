import json
from django.http import HttpResponse, HttpResponseForbidden
from django.views.generic import View
import libraries.utility.cacheproxy as cache
from src.lorepo.token.util import generate_token


class ApiView(View):
    """
        View base object, which requires HTTP Methods to return Python Data Structure for serializing to json.
        Adds to http reponse mimetype
    """

    def dispatch(self, request, *args, **kwargs):
        data = super(ApiView, self).dispatch(request, *args, **kwargs)
        return HttpResponse(json.dumps(data), content_type='application/json')


class TokenApiView(View):
    """
        View base, which adds new crsf token to response under 'token' key in POST method
        response functions should return python dict for serialization

        Inheritting class should implement perfom_action
    """

    token_key = 'Example Token Key'
    token_key_in_dict = 'token'

    def post(self, request, *args, **kwargs):
        token_key = 'token_%s' % self.token_key

        cached_token = cache.get_for_user(request.user, token_key)
        if cached_token is None:
            return HttpResponseForbidden()

        if cached_token is not None:
            cache.delete_for_user(request.user, token_key)

            if self.token_key not in request.POST:
                return HttpResponseForbidden()

            token_value = request.POST.get(self.token_key, "")

            if cached_token != token_value:
                return HttpResponseForbidden()

        data = self.perform_action()

        token = generate_token()
        cache.set_for_user(request.user, token_key, token)

        data[self.token_key_in_dict] = token
        return HttpResponse(json.dumps(data), content_type='application/json')
