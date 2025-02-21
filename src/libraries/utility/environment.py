import os
from djangae.utils import on_production


def get_app_version():
    try:
        # version comes in major.minor format
        major = os.environ['CURRENT_VERSION_ID'].split('.')[0]
        # major on dev server may contain :
        return major.split(':')[0]
    except KeyError:
        return '100'


def get_versioned_module(module_name):
    # locally queue have problem with gce-backend module and throw error.
    if module_name.lower().startswith('gce-backend') and not on_production:
        return get_app_version() + '.' + 'default'
    return get_app_version() + '.' + module_name


def is_development_server():
    return not on_production()


class RequestCache():

    @classmethod
    def init_ram_cache(cls):
        try:
            #make sure ram cache is not persisted between requests
            if not (cls._ram_cache['REQUEST_LOG_ID'] == os.environ.get('REQUEST_LOG_ID')):
                cls._ram_cache = {'REQUEST_LOG_ID': os.environ.get('REQUEST_LOG_ID')}
        except (KeyError, AttributeError) as e:
            if isinstance(e, AttributeError):
                cls._ram_cache = {'REQUEST_LOG_ID': os.environ.get('REQUEST_LOG_ID')}

    @classmethod
    def get(cls, key):
        cls.init_ram_cache()
        return cls._ram_cache.get(key, None)

    @classmethod
    def set(cls, key, value):
        cls.init_ram_cache()
        cls._ram_cache[key] = value

    @classmethod
    def flush(cls):
        cls._ram_cache = {'REQUEST_LOG_ID': os.environ.get('REQUEST_LOG_ID')}
