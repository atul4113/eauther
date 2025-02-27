from src.libraries.utility.environment import is_development_server


def is_request_secure(request):
    if request.is_secure():
        return True

    # Handle the Webfaction case until this gets resolved in the request.is_secure()
    if 'HTTP_X_FORWARDED_SSL' in request.META:
        return request.META['HTTP_X_FORWARDED_SSL'] == 'on'

    if is_development_server():
        return True

    return False
