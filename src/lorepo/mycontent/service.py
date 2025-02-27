from src.lorepo.mycontent.models import Content, ContentSpace
import src.libraries.utility.cacheproxy as cache
from src.lorepo.spaces.service import update_space
from src.lorepo.spaces.models import Space

CONTENT_CACHE_TIMEOUT = 60 * 60 * 24

def get_list_by_ids(ids):
    return list(Content.objects.filter(id__in=list(ids)).order_by('title'))


def add_content_to_space(content, space, is_deleted=False):
    cs = ContentSpace(content=content, space=space)
    cs.is_deleted = is_deleted
    cs.save()
    cs.content.spaces_path = _get_path(space)
    cs.content.spaces = cs.content.spaces_path.split(',')
    cs.content.save()
    cache.delete('content_spaces_for_space_%s' % space.id)
    if not is_deleted:
        _update_contents_count(cs.content.spaces, lambda x: x + 1)
    return cs

def remove_content_space(content_space):
    space_id = content_space.space.id
    _update_contents_count(content_space.content.spaces, lambda x: x - 1)
    content_space.delete()
    content_space.content.spaces_path = ''
    content_space.content.spaces = []
    content_space.content.save()
    cache.delete('content_spaces_for_space_%s' % space_id)

def update_content_space(content_space):
    content_space.save()
    content_space.content.spaces_path = _get_path(content_space.space)
    content_space.content.spaces = content_space.content.spaces_path.split(',')
    content_space.content.save()
    cache.delete('content_spaces_for_space_%s' % content_space.space.id)
    func = (lambda x: x - 1) if content_space.is_deleted else (lambda x: x + 1)
    _update_contents_count(content_space.content.spaces, func)

def _update_contents_count(spaces_id, func):
    for space_id in spaces_id:
        spaces = Space.objects.filter(pk=space_id)
        space = spaces[0] if len(spaces) > 0 else None
        if not space:
            continue
        space.contents_count = func(space.contents_count)
        update_space(space, propagate_update=False) #update propagation would trigger recalculation of access rights for the whole company

def _get_path(space):
    spaces = []
    while not space.is_top_level():
        spaces.append(space)
        space = space.parent
    spaces.append(space)
    spaces.reverse()
    ids = [str(space.id) for space in spaces]
    return ','.join(ids)

def get_content_ids_from_space(space):
    ids = cache.get('content_spaces_for_space_%s' % space.id)
    if ids is None:
        ids = space.contentspace_set.filter(is_deleted=False).values_list('content', flat=True)
        cache.set('content_spaces_for_space_%s' % space.id, ids, CONTENT_CACHE_TIMEOUT)
    return ids