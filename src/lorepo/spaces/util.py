import src.libraries.utility.cacheproxy as cache
from django.core.mail import mail_admins
from src.lorepo.mycontent.models import ContentLike, Content
from src.lorepo.mycontent.service import get_list_by_ids, add_content_to_space,\
    remove_content_space
from src.lorepo.permission.models import PermissionTuples, Role
from src.lorepo.spaces.models import Space, SpaceAccess, SpaceType,\
    LockedSpaceAccess, AccessRightType, UserSpacePermissions
from src.lorepo.spaces.service import get_space_list_by_ids


def filter_deleted(spaces, subspaces=None, is_trash=False):
    '''Divides content into collection of deleted and collection of not deleted ones.
    Not deleted ones are additionally filtered based on a subspaces.
    '''
    deleted = []
    content_list = []
    total = 0
    for space in spaces:
        not_deleted = space.contentspace_set.filter(is_deleted=False).values_list('content', flat=True)
        not_deleted_contents = get_list_by_ids(not_deleted)
        space.size = len(not_deleted_contents)
        total += len(not_deleted_contents)

        if is_trash:
            deleted_contents = [cs.content for cs in space.contentspace_set.filter(is_deleted=True)]
            deleted.extend(deleted_contents)
        if subspaces and space not in subspaces:
            continue
        content_list.extend(not_deleted_contents)

    return content_list, deleted, total


def get_space_for_content_cached(content):
    space = cache.get('get_space_for_content_cached_%s' % content.pk)

    if space is None:
        space = get_space_for_content(content)
        cache.set('get_space_for_content_cached_%s' % content.pk, space, 30)

    return space


def get_space_for_content(content):
    '''Gets the private space that content is associated with.
    '''
    contentspaces = content.contentspace_set.all()
    spaces = [cs.space for cs in contentspaces if not cs.space.is_public()]
    if len(spaces) == 0:
        raise Exception('Content <%(title)s> is not associated with any space' % {'title' : content.title})
    else:
        if len(spaces) > 1:
            mail_admins('Content Space error', 
                        'Content <%(title)s> [%(content_id)s] is associated with more than one private space'
                         % {'title' : content.title, 'content_id' : content.pk })
        return spaces[0]


def get_public_space_for_content(content):
    '''Gets the public space that content is associated with.
    '''
    contentspaces = content.contentspace_set.filter(is_deleted=False)
    spaces = [cs.space for cs in contentspaces if cs.space.is_public()]
    if len(spaces) > 1:
        raise Exception('Content is associated with more than one public space')
    else:
        return spaces[0] if len(spaces) > 0 else None

def get_private_space_for_user(user):
    '''Get top level private space for user
    '''
    try:
        for sa in user.spaceaccess_set.all():
            if sa.space.is_private() and sa.space.is_top_level():
                return sa.space
    except AttributeError:
        # Handle case where user model doesn't have spaceaccess_set
        return None

    raise Exception('No private space for user %(user)s' % {'user' : user.username})


def get_private_space_for_user_cached(user):
    space = cache.get("get_private_space_for_user_cached_space_%s" % (user.id))
    if space:
        return space

    space = get_private_space_for_user(user)
    cache.set("get_private_space_for_user_cached_space_%s" % (user.id), space, 30)
    return space


def _get_subspaces(spaces, is_deleted=False):
    tmp = set()
    for s in spaces:
        tmp.update(Space.objects.filter(path=s.id, is_deleted=is_deleted))
    return tmp


def get_cached_kids(space_id, is_deleted = False):
    kids = cache.get('kid_spaces_for_%s' % space_id)
    if not kids:
        kids = Space.objects.filter(parent__id=space_id, is_deleted=is_deleted).order_by('rank')
        cache.set('kid_spaces_for_%s' % space_id, kids, 60 * 60 * 24)
    return kids


def load_kids(spaces, recursive = True, is_deleted = False):
    for space in spaces:
        space.loaded_kids = get_cached_kids(space.id, is_deleted)
        if recursive:
            load_kids(space.loaded_kids)


def get_lessons(space):
    lessons = []
    for content in Content.objects.filter(spaces=str(space.id), is_deleted=False).order_by('title'):
        content_spaces = content.spaces_path.split(',')
        if content_spaces[len(content_spaces)-1] != str(space.id):
            continue
        lesson = {}
        lesson['lesson-id'] = content.id
        lesson['name'] = content.title
        lesson['version'] = str(content.file.version)
        lessons.append(lesson)
    return lessons


def structure_as_dict(space):
    space.loaded_kids = cache.get('kid_spaces_for_%s' % space.id)
    if space.loaded_kids is None:
        space.loaded_kids = space.kids.filter(is_deleted = False).order_by('rank')
        cache.set('kid_spaces_for_%s' % space.id, space.loaded_kids, 60 * 60 * 24)

    kids = []
    for s in space.loaded_kids:
        kid = structure_as_dict(s)
        kids.append(kid)

    space_entry = {
        'name': space.title,
    }

    lessons = get_lessons(space)
    if len(lessons):
        space_entry['lessons'] = lessons

    if len(kids):
        space_entry['kids'] = kids

    return space_entry


def structure_with_ids_as_dict(space, recursive=True):
    space.loaded_kids = cache.get('kid_spaces_for_%s' % space.id)
    if space.loaded_kids is None:
        space.loaded_kids = space.kids.filter(is_deleted=False).order_by('rank')
        cache.set('kid_spaces_for_%s' % space.id, space.loaded_kids, 60 * 60 * 24)

    kids = []

    if recursive:
        for s in space.loaded_kids:
            kid = structure_with_ids_as_dict(s)
            kids.append(kid)

    else:
        for s in space.loaded_kids:
            kid = {
                'name': s.title,
                'id': s.id
            }
            kids.append(kid)

    space_entry = {
        'name': space.title,
        'id': space.id
    }

    if len(kids):
        space_entry['subspaces'] = kids

    return space_entry

def get_all_user_spaces(user): #this only returns spaces up to some level of nesting
    all_spaces = get_user_spaces(user)
    all_spaces.update(get_corporate_spaces_for_user(user))
    return all_spaces


def get_user_spaces(user):
    '''Get all user spaces and their subspaces.
    '''
    spaces = set()
    ids = SpaceAccess.objects.filter(user__id=user.id).values_list('space', flat=True)
    all_spaces = get_space_list_by_ids(ids)
    for s in all_spaces:
        if s.is_private():
            spaces.add(s)
    spaces.update(_get_subspaces(spaces))
    return spaces


def get_corporate_spaces_for_user(user):
    spaces = set()
    ids = SpaceAccess.objects.filter(user__id=user.id).values_list('space', flat=True)
    all_spaces = get_space_list_by_ids(ids)
    for s in all_spaces:
        if s.is_corporate():
            spaces.add(s)
    spaces.update(_get_subspaces(spaces))
    return spaces


def get_spaces_tree(space_id):
    spaces = set()
    space = Space.objects.get(pk=space_id)
    if not space.is_top_level():
        spaces.add(space.top_level)
    else:
        spaces.add(space)
    spaces.update(_get_subspaces(spaces))
    return spaces


def get_spaces_subtree(space_id, is_deleted=False):
    spaces = set()
    space = Space.objects.get(pk=space_id)
    spaces.add(space)
    spaces.update(_get_subspaces(spaces, is_deleted))
    return spaces


def get_top_level_owned_corporate_spaces(user):
    spaces = set()
    for sa in user.spaceaccess_set.all():
        if sa.isOwner() and sa.space.is_corporate():
            spaces.add(sa.space)
    return spaces


def get_owned_corporate_spaces_for_user(user):
    spaces = set()
    for sa in user.spaceaccess_set.all():
        if sa.isOwner() and sa.space.is_corporate():
            spaces.add(sa.space)

    spaces.update(_get_subspaces(spaces))
    return spaces


def get_second_level_corporate_spaces_for_user(user):
    return [space for space in get_corporate_spaces_for_user(user) if space.is_second_level()]


def get_spaces_for_copy(user):
    spaces = cache.get_for_user(user, 'copy_spaces')
    if spaces is None:
        spaces = [division for division in list(user.divisions.values()) if division.kids.filter(is_deleted=False)]
        cache.set_for_user(user, 'copy_spaces', spaces, 60*60*24)
    return spaces


def get_top_level_public_spaces():
    return Space.objects.filter(space_type=SpaceType.PUBLIC, parent=None)


def get_top_level_corporate_spaces(space_filter = None):
    companies = Space.objects.filter(space_type=SpaceType.CORPORATE, parent=None).order_by('title')
    if space_filter:
        return [company for company in companies if space_filter(company)]
    return companies


def get_content_like(content, request):
    ip = request.META['REMOTE_ADDR']
    if ContentLike.objects.filter(content=content, ip=ip).count() > 0:
        cl = ContentLike.objects.get(content=content, ip=ip)
        like = cl.like
    else: 
        like = None
    return like


def change_contentspace(content, space_id, is_public):
    if is_public:
        space = get_public_space_for_content(content)
        if space is not None:
            for current_contentspace in content.contentspace_set.filter(space=space):
                remove_content_space(current_contentspace)
        if space_id is not None:
            new_space = Space.objects.get(pk=space_id)
            return add_content_to_space(content, new_space)
    else:
        space = get_space_for_content(content)
        current_content_spaces = content.contentspace_set.filter(space=space)
        if space_id is not None:
            if space.id == space_id:
                return current_content_spaces[0]
            for current_contentspace in current_content_spaces:
                remove_content_space(current_contentspace)
            new_space = Space.objects.get(pk=space_id)
            return add_content_to_space(content, new_space)


def get_contents_and_total(spaces, subspaces, contents):
    total = 0
    subtotal = 0
    for space in spaces:
        content_spaces = space.contentspace_set.all()
        space.loaded_kids = space.kids.all()
        subtotal = get_contents_and_total(space.loaded_kids, subspaces, contents)
        public_content_spaces = [cs for cs in content_spaces if cs.content.is_content_public()]
        total += len(public_content_spaces) + subtotal
        space.size = len(public_content_spaces) + subtotal
        for cs in public_content_spaces:
            if space in subspaces:
                contents.append(cs.content)
    return total


def get_spaces_path_for_content(content, space_filter):
    ''' Gets the spaces path for a given content.
    Path is a list of Space object in order from top level
    down to the space that the content is associated with.

    space_filter is a lambda used to filter the spaces, ie. to filter
    public spaces only pass 'lambda space: space.is_public()'
    '''
    space = None
    spaces = []
    for cs in content.contentspace_set.all():
        if space_filter(cs.space):
            space = cs.space
            spaces.append(space)
            break

    while space and not space.is_top_level():
        space = space.top_level
        spaces.append(space)
    spaces.reverse()

    return spaces


def has_space_permission(space, user, permission):
    sa = get_space_access(space, user)
    return sa.has_permission(permission) if sa is not None else False


def is_space_owner(space, user):
    usp = UserSpacePermissions.get_cached_usp_for_user(user)
    return usp.has_owner_role_for_space(space.id)
def get_space_access(space, user):
    if not space or not user:
        return None

    if user.is_superuser and space.is_corporate():
        superuser = None
        all_permissions = []
        for k, v in list(PermissionTuples.items()):
            all_permissions.append(k)

        all_permissions.sort()
        roles = Role.objects.filter(company=space.top_level)

        for role in roles:
            if all_permissions == sorted(role.permissions):
                superuser = role
                break
        if superuser is None:
            return None

        return SpaceAccess(user=user, space=space, access_right=AccessRightType.OWNER, roles=[superuser.id])

    sa = get_cached_space_access(space.id, user.id)
    if sa is None:
        if space.parent is not None:
            parent_space = space.parent
            while sa is None and parent_space is not None:
                sa = get_cached_space_access(parent_space.id, user.id)
                parent_space = parent_space.parent
    return sa


def get_cached_space_access(space_id,user_id):
    sa = cache.get("space_access_%s_%s" % (space_id, user_id))
    if sa is not None:
        return sa
    space_access = SpaceAccess.objects.filter(user__id=user_id, space__id=space_id, is_deleted = False)
    if len(space_access) > 0:
        sa = space_access[0]
        cache.set("space_access_%s_%s" % (space_id, user_id), sa, 60 * 30) #cache whole user sa instead of just one
    return sa


class SpacePermissionGenerator(object):

    def __init__(self, user_id, new_space_id, action):
        self.user_id = user_id
        self.space_access_list = []
        self.roles = {}

        self.space_access_list = list(SpaceAccess.objects.filter(user__id=user_id, is_deleted=False)) #cache this whole list
        if new_space_id:
            new_space_access = get_cached_space_access(new_space_id, user_id) #new space_access can be in cache before it's visible in the DB
            if new_space_access:
                self.space_access_list.append(new_space_access)
            else:
                if action == 'delete':
                    self.space_access_list = [sa for sa in self.space_access_list if sa.space_id != new_space_id]


    def calculate_space_permissions(self, usp):
        for space_access in self.space_access_list:
            permissions = []
            for role_id in space_access.roles:
                permissions += self._get_ramcached_role(role_id).permissions
            permissions = list(set(permissions))
            usp.add_space_permissions(space_access.space_id, permissions)
            descendants = self.space_map.descendants_for_space_id(space_access.space_id)
            for leaf_id in descendants:
                usp.add_space_permissions(leaf_id, permissions)


    def _get_ramcached_role(self, role_id):
        try:
            return self.roles[role_id]
        except:
            role = Role.get_cached_role(role_id)
            self.roles[role_id] = role
            return role


    def set_map(self, company_space_map):
        self.space_map = company_space_map
        self.space_map.set_private(self.get_private_space())


    def user_spaces_ids(self):
        try:
            return self._user_space_ids
        except:
            self._user_space_ids = []
            for space_access in self.space_access_list:
                self._user_space_ids.append(space_access.space_id)
                self._user_space_ids.extend(self.space_map.descendants_for_space_id(space_access.space_id))
            self._user_space_ids = list(set(self._user_space_ids))
            return self._user_space_ids

    def get_private_space(self):
        for sa in self.space_access_list:
            if sa.space.is_private() and sa.space.is_top_level():
                return sa.space
        raise Exception('No private space for user %(user)s' % {'user' : self.space_access_list[0].user.username})


def get_users_from_space(space):
    space_accesses = SpaceAccess.objects.filter(space=space)
    users = [sa.user for sa in space_accesses]
    return users


def get_spaces_from_top_to_specific_space(space):
    spaces = [space.top_level]
    while not space.is_top_level():
        spaces.append(space)
        space = space.parent
    return spaces


def get_space_type(content):
    space = get_space_for_content(content)
    if content.is_content_public():
        return 'public'
    elif space.is_corporate():
        return 'corporate'
    else:
        return 'mycontent'


def get_locked_companies(user):
    lsas = LockedSpaceAccess.objects.filter(user = user)
    locked_companies = [lsa.space.top_level for lsa in lsas]
    return set(locked_companies)


def is_company_locked(name):
    for locked_space_access in LockedSpaceAccess.objects.filter(space = name):
        if locked_space_access.space == name:
            return True
    return False

def get_projects_with_publications(request, sort_function, limit = None):
    spaces = []
    for space in list(request.user.divisions.values())[:limit]:
        space.loaded_kids = cache.get('kid_spaces_for_%s' % space.id)
        if space.loaded_kids is None:
            space.loaded_kids = sorted(space.kids.filter(is_deleted = False), key = sort_function)
            cache.set('kid_spaces_for_%s' % space.id, space.loaded_kids, 60 * 60 * 24)
        spaces.append(space)
    return spaces
