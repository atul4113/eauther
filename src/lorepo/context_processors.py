import settings as global_settings


def settings(_):
    return {'settings': global_settings}


def urls(_):
    return {'BASE_URL': global_settings.BASE_URL, 'BASE_SECURE_URL': global_settings.MAUTHOR_BASIC_URL}