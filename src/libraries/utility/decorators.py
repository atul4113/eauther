import logging
import datetime
from django.contrib.auth.decorators import user_passes_test
from django.http import Http404
from django.utils.decorators import method_decorator
from google.appengine.api.modules import get_current_module_name
from libraries.utility import cacheproxy as cache
from libraries.utility.environment import RequestCache, is_development_server
from google.appengine.api import urlfetch
from django.conf import settings

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
        if get_current_module_name() == 'default':
            if not request.META['SERVER_SOFTWARE'].startswith('Development'):
                raise Http404
        return function(request, *args, **kwargs)
    return _wrapper

def localhost_required(function):
    def _wrapper(request, *args, **kwargs):
        if not request.META['SERVER_SOFTWARE'].startswith('Development'):
            raise Http404
        return function(request, *args, **kwargs)
    return _wrapper

def service_admin_user(function):
    def _wrapper(request, *args, **kwargs):
        if not request.META['SERVER_SOFTWARE'].startswith('Development'):
            try:
                # remove 'Bearer TOKEN' from token
                token = request.META['HTTP_AUTHORIZATION'].replace('Bearer ', '', 1)
            except Exception:
                raise Http404
            # https://developers.google.com/identity/protocols/OAuth2UserAgent
            result = urlfetch.fetch(
                url='https://www.googleapis.com/oauth2/v3/tokeninfo?access_token=%s' % token,
                method=urlfetch.GET)
            import json
            loaded_dict = json.loads(result.content)
            if not loaded_dict['email'] == settings.FLEXIBLE_SERVICE_ACCOUNT:
                raise Http404
        return function(request, *args, **kwargs)
    return _wrapper

class SuperUserRequiredMixin(object):
    """
        View mixin which requires user to be super user
    """

    @method_decorator(user_passes_test(lambda user: user.is_superuser))
    def dispatch(self, request, *args, **kwargs):
        return super(SuperUserRequiredMixin, self).dispatch(request, *args, **kwargs)


class BackendMixin(object):

    def dispatch(self, request, *args, **kwargs):
        if get_current_module_name() == 'default':
            if not request.META['SERVER_SOFTWARE'].startswith('Development'):
                raise Http404

        return super(BackendMixin, self).dispatch(request, *args, **kwargs)


def cron_method(handler):
    def check_if_cron(request, *args, **kwargs):
        if not is_development_server():
            return handler(request, *args, **kwargs)
        if request.META.get('HTTP_X_APPENGINE_CRON') is None:
            raise Http404
        return handler(request, *args, **kwargs)
    return check_if_cron


class params2str(object):

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
            key += ','.join(args)
        if kwargs:
            kwargs_keys = []
            for k, v in list(kwargs.items()):
                kwargs_keys.append('%s=%s' % (k, v))
            key += ','.join(kwargs_keys)
    return key


def cached(timeout=60, params_key=None):
    """
    Decorator that store in cache result of target function
    Note: use short timeout or write emptying cache on your own
    To flush cached value call: func.delete_cached(*args like in func)
    :param timeout: time in seconds that value should be stored in cache
    :param params_key: function that makes dynamic part of cache key depends on function arguments
    :return: result of function - faster for subsequent calls
    """
    def outer_wrapper(func):
        def _delete_cached(*args, **kwargs):
            cache_key = func.__name__ + '_' + build_dynamic_key(params_key, args, kwargs)
            cache.delete(cache_key)

        def inner_wrapper(*args, **kwargs):
            cache_key = func.__name__ + '_' + build_dynamic_key(params_key, args, kwargs)
            response = cache.get(cache_key)
            if response is None:
                response = func(*args, **kwargs)
                cache.set(cache_key, response, timeout)
            return response
        inner_wrapper.delete_cached = _delete_cached
        return inner_wrapper
    return outer_wrapper


def cached_in_request(params_key=None):
    """
    Decorator that store in instance's ram result of target function for a single request
    :param params_key: function that makes dynamic part of cache key depends on function arguments
    :return: result of function - faster for subsequent calls
    """
    def outer_wrapper(func):
        def inner_wrapper(*args, **kwargs):
            cache_key = func.__name__ + '_' + build_dynamic_key(params_key, args, kwargs)
            response = RequestCache.get(cache_key)
            if response is None:
                response = func(*args, **kwargs)
                RequestCache.set(cache_key, response)
            return response
        return inner_wrapper
    return outer_wrapper


# From Django 1.8
class cached_property(object):
    """
    Decorator that converts a method with a single self argument into a
    property cached on the instance.

    Optional ``name`` argument allows you to make cached properties of other
    methods. (e.g.  url = cached_property(get_absolute_url, name='url') )
    """
    def __init__(self, func, name=None):
        self.func = func
        self.__doc__ = getattr(func, '__doc__')
        self.name = name or func.__name__

    def __get__(self, instance, type=None):
        if instance is None:
            return self
        res = instance.__dict__[self.name] = self.func(instance)
        return res
