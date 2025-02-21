import re

MOBILE_AGENT_PATTERN = re.compile("Android|BlackBerry|iPhone|iPad|iPod|IEMobile|Opera Mini", re.IGNORECASE)
SAFARI_MOBILE_AGENT_PATTERN = re.compile("iPhone|iPad|iPod", re.IGNORECASE)


def is_mobile_user_agent(request):
    ua = _get_user_agent(request)

    if ua == '':
        return False

    if MOBILE_AGENT_PATTERN.search(ua):
        return True
    else:
        return False


def is_ios_user_agent(request):
    ua = _get_user_agent(request)

    if ua == '':
        return False

    if SAFARI_MOBILE_AGENT_PATTERN.search(ua):
        return True
    else:
        return False


def _get_user_agent(request):
    if not hasattr(request, 'META'):
        return ''

    return request.META.get('HTTP_USER_AGENT', '')