from lorepo.spaces.models import Space
import libraries.utility.cacheproxy as cache
from lorepo.spaces.signals import company_structure_has_changed

SPACE_CACHE_TIMEOUT = 60 * 60 * 24

def get_space_list_by_ids(ids):
    ids = list(ids)
    contents = cache.get_many(ids)
    missing_ids = list(set(ids) - set(contents.keys()))
    contents = list(contents.values())
    if missing_ids:
        fresh_contents = list(Space.objects.filter(id__in=missing_ids, is_deleted=False))
        contents.extend(fresh_contents)
        my_dict = {}
        for content in contents:
            my_dict[content.id] = content
        cache.set_many(my_dict, SPACE_CACHE_TIMEOUT)
    return contents

def insert_space(space):
    space.save() #this save here is necessary because we might need the id in the while loop
    path = []
    parent = space
    while not parent.is_top_level():
        path.append(parent.id)
        parent = parent.parent
    path.append(parent.id)
    path.reverse()
    space.path = path
    space.save()
    if space.parent is not None:
        cache.delete('kid_spaces_for_%s' % space.parent_id)
        if space.is_corporate():
            company_structure_has_changed.send(None, company_id = space.top_level_id)

def update_space(space, propagate_update = True):
    if propagate_update:
        insert_space(space)
    else:
        space.save()
    if space.parent:
        cache.delete('kid_spaces_for_%s' % space.parent.id)
    return cache.set(space.id, space, SPACE_CACHE_TIMEOUT)