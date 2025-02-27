import logging
import datetime
import requests
from django.contrib.auth.decorators import user_passes_test
from django.http import Http404
from django.utils.decorators import method_decorator
from django.conf import settings
from src.libraries.utility import cacheproxy as cache
from src.libraries.utility.environment import RequestCache, is_development_server


def log_time(fn):
    def wrapped(*args, **kwargs):
        start = datetime.datetime.now()
        result = fn(*args, **kwargs)
        end = datetime.datetime.now()
        logging.info("%s.%s [%s]", fn.__module__, fn.__name__, end - start)
        return result

    return wrapped


def backend(function):
    def _wrapper(request, *args, **kwargs):
        if not settings.DEBUG:
            raise Http404
        return function(request, *args, **kwargs)

    return _wrapper


def localhost_required(function):
    def _wrapper(request, *args, **kwargs):
        if not settings.DEBUG:
            raise Http404
        return function(request, *args, **kwargs)

    return _wrapper


def service_admin_user(function):
    def _wrapper(request, *args, **kwargs):
        if not settings.DEBUG:
            try:
                token = request.META['HTTP_AUTHORIZATION'].replace('Bearer ', '', 1)
            except KeyError:
                raise Http404

            response = requests.get(
                f'https://www.googleapis.com/oauth2/v3/tokeninfo?access_token={token}'
            )

            if response.status_code != 200:
                raise Http404

            loaded_dict = response.json()
            if loaded_dict.get('email') != settings.FLEXIBLE_SERVICE_ACCOUNT:
                raise Http404
        return function(request, *args, **kwargs)

    return _wrapper


class SuperUserRequiredMixin:
    """
    View mixin which requires user to be super user
    """

    @method_decorator(user_passes_test(lambda user: user.is_superuser))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class BackendMixin:
    def dispatch(self, request, *args, **kwargs):
        if not settings.DEBUG:
            raise Http404
        return super().dispatch(request, *args, **kwargs)


def cron_method(handler):
    def check_if_cron(request, *args, **kwargs):
        if not is_development_server():
            return handler(request, *args, **kwargs)
        if request.META.get('HTTP_X_APPENGINE_CRON') is None:
            raise Http404
        return handler(request, *args, **kwargs)

    return check_if_cron


class params2str:
    @staticmethod
    def objects_ids(*args):
        return ','.join(str(u.id) for u in args)

    @staticmethod
    def dict_ids(*args):
        return ','.join(str(u['id']) for u in args)


def build_dynamic_key(params_key, args, kwargs):
    key = ''
    if params_key:
        key += params_key(*args, **kwargs)
    else:
        if args:
            key += ','.join(map(str, args))
        if kwargs:
            key += ','.join(f'{k}={v}' for k, v in kwargs.items())
    return key


def cached(timeout=60, params_key=None):
    def outer_wrapper(func):
        def _delete_cached(*args, **kwargs):
            cache_key = f"{func.__name__}_{build_dynamic_key(params_key, args, kwargs)}"
            cache.delete(cache_key)

        def inner_wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}_{build_dynamic_key(params_key, args, kwargs)}"
            response = cache.get(cache_key)
            if response is None:
                response = func(*args, **kwargs)
                cache.set(cache_key, response, timeout)
            return response

        inner_wrapper.delete_cached = _delete_cached
        return inner_wrapper

    return outer_wrapper


def cached_in_request(params_key=None):
    def outer_wrapper(func):
        def inner_wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}_{build_dynamic_key(params_key, args, kwargs)}"
            response = RequestCache.get(cache_key)
            if response is None:
                response = func(*args, **kwargs)
                RequestCache.set(cache_key, response)
            return response

        return inner_wrapper

    return outer_wrapper


class cached_property:
    """
    Decorator that converts a method with a single self argument into a
    property cached on the instance.
    """

    def __init__(self, func, name=None):
        self.func = func
        self.__doc__ = func.__doc__
        self.name = name or func.__name__

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        res = instance.__dict__[self.name] = self.func(instance)
        return res
