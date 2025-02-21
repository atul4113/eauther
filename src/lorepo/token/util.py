import random
from functools import partial

import libraries.utility.cacheproxy as cache
from lorepo.token.models import TOKEN_KEYS


def generate_token(token_size=5):
    token = ''
    while token_size > 0:
        ascii_range = random.randint(1, 3)
        if ascii_range == 1:
            random_char = chr(random.randint(48, 57))
        elif ascii_range == 2:
            random_char = chr(random.randint(65, 90))
        else:
            random_char = chr(random.randint(97, 122))
        token += random_char
        token_size -= 1
        
    return token


def create_and_cache_token(user, key=""):
    """Returns token, token_key"""
    token_key = 'token_{0}'.format(key)
    token = generate_token()
    cache.set_for_user(user, token_key, token)

    return token, token_key

create_publication_action_token = partial(create_and_cache_token, key=TOKEN_KEYS.PUBLICATION_ACTION)
create_mycontent_editor_token = partial(create_and_cache_token, key=TOKEN_KEYS.MYCONTENT_EDITOR)
create_project_states_token = partial(create_and_cache_token, key=TOKEN_KEYS.PROJECT_STATES)
create_mycontent_edit_addon_token = partial(create_and_cache_token, key=TOKEN_KEYS.MYCONTENT_EDIT_ADDON)
create_kanban_token = partial(create_and_cache_token, key=TOKEN_KEYS.KANBAN)
