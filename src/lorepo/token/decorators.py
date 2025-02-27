from django.http import HttpResponseForbidden
from src.lorepo.token.util import generate_token, create_and_cache_token
from django.shortcuts import render
import src.libraries.utility.cacheproxy as cache


def token(key, method=None):
    def _inner(function):
        session_key = 'token_%s' % key

        def _wrapper(request, *args, **kwargs):
            if session_key not in request.session:
                request.session[session_key] = generate_token()
                response = function(request, *args, **kwargs)
                return response

            session_token = str(request.session[session_key])

            if session_token == request.GET.get('_TOKEN'):
                request.session[session_key] = generate_token()
            elif '_TOKEN' in request.GET:
                return render(request, 'token/double-click.html', {
                    'go_back': request.META['HTTP_REFERER'] if 'HTTP_REFERER' in request.META else '/'
                })

            return function(request, *args, **kwargs)
        return _wrapper
    if hasattr(method, '__call__'):
        return _inner(method)
    return _inner


def cached_token(token_key):
    def _inner(function):
        def _wrapper(request, *args, **kwargs):
            token_mixin = TokenMixin()
            token_mixin.token_key = token_key
            if not token_mixin.check_tokens_are_match(request, *args, **kwargs):
                redirect_to = request.GET.get("next")
                return render(request, 'token/bad-token.html', {
                    'go_back': redirect_to
                })
            return function(request, *args, **kwargs)
        return _wrapper
    return _inner


def get_form_token_cache_key(key):
    return 'token_%s' % key


def get_form_token(user, key):
    return cache.get_for_user(user, get_form_token_cache_key(key))


def set_form_token(user, key):
    cache.set_for_user(user, get_form_token_cache_key(key), generate_token())


def remove_form_token(user, key):
    cache.delete_for_user(user, get_form_token_cache_key(key))


def form_token(key):
    def _inner(function):
        def _wrapper(request, *args, **kwargs):
            def _render_invalid_token_response(req):
                return render(req, 'token/invalid_token.html', {
                    'next_url': req.META['HTTP_REFERER'] if 'HTTP_REFERER' in req.META else '/'
                })

            if request.method == "GET":
                set_form_token(request.user, key)
            else:
                cached_token = get_form_token(request.user, key)

                if cached_token:
                    remove_form_token(request.user, key)

                    if not key in request.POST:
                        return _render_invalid_token_response(request)

                    form_token_value = request.POST[key]
                    if cached_token != form_token_value:
                        return _render_invalid_token_response(request)
                else:
                    return _render_invalid_token_response(request)

            return function(request, *args, **kwargs)
        return _wrapper
    return _inner


class TokenMixin(object):
    """
        Mixin which requires user to have valid crsf token in request method specified by token_methods
    """

    token_key = 'Example Token Key'
    methods = ["POST", "GET"]

    def dispatch(self, request, *args, **kwargs):
        if self.check_tokens_are_match(request, *args, **kwargs):
            return super(TokenMixin, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponseForbidden()

    def check_tokens_are_match(self, request, *args, **kwargs):
        if request.method not in self.methods:
            return True

        cached_token = self.get_cached_token(request)
        client_token = self.get_client_token(request)

        if client_token == cached_token:
            self.delete_cached_token(request, cached_token)
            return True

        return False

    def get_token_key(self):
        token_key = 'token_{0}'.format(self.token_key)
        return token_key

    def get_client_token(self, request):
        if request.method == "GET":
            return request.GET.get(self.get_token_key())
        if request.method == "POST":
            return request.POST.get(self.get_token_key())

    def get_cached_token(self, request):
        user = request.user
        token_key = self.get_token_key()
        cached_token = cache.get_for_user(user, token_key)
        if cached_token is None:
            return HttpResponseForbidden()
        return cached_token

    def delete_cached_token(self, request, cached_token):
        if cached_token is not None:
            cache.delete_for_user(request.user, self.get_token_key())


class AddContextTokenMixin(object):

    context_token_key = "token_key"
    token_key = 'Example Token Key'

    def get_context_data(self, **kwargs):
        context_data = super(AddContextTokenMixin, self).get_context_data(**kwargs)

        if not self.token_key in context_data:
            context_data[self.token_key] = create_and_cache_token(self.request.user, self.token_key)
            context_data[self.context_token_key] = self.token_key

        return context_data