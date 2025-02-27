from urllib.parse import quote
from django.http import HttpResponseRedirect
from src.lorepo.mycontent.models import Content

def is_being_edited(function):
    '''
    This decorator will translate content_id or addon_id from kwargs to content or addon.
    :param function:
    :return:
    '''
    def _wrapper(request, *args, **kwargs):
        if ('content_id' not in kwargs) and ('addon_id' not in kwargs):
            return function(request, *args, **kwargs)

        if 'addon_id' in kwargs:
            what_editing = 'add'
        else:
            what_editing = 'less'

        try:
            content_id = kwargs.pop('content_id')
            content = Content.get_cached_or_404(id = content_id)
            kwargs['content'] = content
        except KeyError:
            pass
        try:
            content_id = kwargs.pop('addon_id')
            content = Content.get_cached_or_404(id = content_id)
            kwargs['addon'] = content
        except KeyError:
            pass

        if request.method == 'GET':
            confirmed = request.GET.get('confirmed', None)
            user = content.who_is_editing()
            full_url = request.get_full_path()
            encoded_full_url = quote(full_url)
            if not user or confirmed:
                content.set_user_is_editing(request.user)
                return function(request, *args, **kwargs)
            elif request.user == user and what_editing == 'less':
                redirect_url = '/mycontent/{}/confirm_self_editing?next_url={}'.format(content_id, encoded_full_url)
            elif request.user == user and what_editing == 'add':
                redirect_url = '/mycontent/{}/confirm_self_editing_addon?next_url={}'.format(content_id, encoded_full_url)
            else:
                redirect_url = '/mycontent/{}/confirm_editing?next_url={}&who={}'.format(content_id, encoded_full_url, user)

            back_url = request.REQUEST.get("next")
            if back_url is not None:
                redirect_url = redirect_url + '&back_url={}'.format(back_url)

            return HttpResponseRedirect(redirect_url)

        else:
            result = function(request, *args, **kwargs)
            content.stop_editing(request.user)
            return result
    return _wrapper


class IsBeingEdited(object):
    SELF_EDITING_URL = '/mycontent/{}/confirm_self_editing?next_url={}&next={}'
    ANOTHER_USER_EDITING_URL = '/mycontent/{}/confirm_editing?next_url={}&who={}&next={}'

    def __init__(self, content_id_name='content_id', confirmed_name='confirmed'):
        self.content_id_name = content_id_name
        self.confirmed_name = confirmed_name

    def __call__(self, f):
        def wrapper(*args, **kwargs):
            request = args[0]
            content_id = kwargs.get(self.content_id_name)
            content = Content.get_cached_or_404(id=content_id)
            user = content.who_is_editing()
            encoded_full_url = quote(request.get_full_path())
            confirmed = request.GET.get(self.confirmed_name, None)

            if user is None or confirmed:
                content.set_user_is_editing(request.user)
                return f(*args, **kwargs)
            else:
                next = request.GET.get('next', '/mycontent')

                if user == request.user:
                    redirect_url = self.SELF_EDITING_URL.format(content_id, encoded_full_url, next)
                else:
                    redirect_url = self.ANOTHER_USER_EDITING_URL.format(content_id, encoded_full_url, user, next)

                back_url = request.GET.get("next")
                if back_url is not None:
                    redirect_url = redirect_url + '&back_url={}'.format(back_url)

            return HttpResponseRedirect(redirect_url)

        return wrapper
