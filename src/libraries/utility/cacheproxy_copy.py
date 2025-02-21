from django.core.cache import cache
import hashlib

def set_for_user(user, name, value, timeout=None):
    return True
    # return cache.set(_get_key(user, name), value, timeout)

def get_for_user(user, name):
    return cache.get(_get_key(user, name))

def delete_for_user(user, name):
    # return True
    return cache.delete(_get_key(user, name))

def get_many_as_list(names):
    return []
    # return cache.get_many(names).values()

def get_many(names):
    return {}
    # return cache.get_many(names)

def set_many(names_values, timeout=None):
    return True
    # return cache.set_many(names_values, timeout)

def set(name, value, timeout=None):
    return True
    # return cache.set(name, value, timeout)

def get(name):
    return None
    # return cache.get(name)

def delete(name):
    # return True
    return cache.delete(name)

def _get_key(user, name):
    return '%(name)s_%(user)s' % {'name' : name, 'user' : user.username}

def delete_template_fragment_cache(fragment_name='', *args):
    my_hash = hashlib.new('md5')
    my_hash.update(':'.join([str(arg) for arg in args]))
    cache.delete('template.cache.%s.%s' % (fragment_name, my_hash.hexdigest()))

def own_cache_mutex_try(name):
    if get(name):
        return False
    else:
        set(name,True)
        return True

def free_cache_mutex(name):
    delete(name)
