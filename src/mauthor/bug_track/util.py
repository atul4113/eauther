from lorepo.spaces.util import get_spaces_from_top_to_specific_space, get_users_from_space
from mauthor.bug_track.models import Bug

def get_users_for_email(space):
    spaces = get_spaces_from_top_to_specific_space(space)
    users = set()
    for space in spaces:
        users.update(set(get_users_from_space(space)))
    return users

def get_last_bug_for_content(content):
    bug = Bug.objects.filter(content__id=content.id).order_by('-created_date')
    return bug[0] if len(bug) > 0 else None