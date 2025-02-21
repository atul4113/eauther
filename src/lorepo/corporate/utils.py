from lorepo.corporate.models import CorporateLogo
from lorepo.mycontent.models import ContentSpace, Content
from lorepo.spaces.util import get_spaces_subtree
from django.conf import settings
from lorepo.filestorage.utils import resize_image
from google.appengine.ext.blobstore import create_gs_key


def set_uploaded_file(uploaded_file, user, corporate_logo_list, space, content_type):
    uploaded_file.owner = user
    uploaded_file.content_type = content_type

    uploaded_file.save()
    uploaded_file.path = resize_image(uploaded_file, settings.LOGO_SIZE["width"], settings.LOGO_SIZE["height"])
    uploaded_file.file = str(create_gs_key('/gs' + uploaded_file.path))
    uploaded_file.save()

    if len(corporate_logo_list) == 0:
        cl = CorporateLogo(logo=uploaded_file, space=space)
    else:
        cl = corporate_logo_list[0]
        cl.logo = uploaded_file
    cl.save()


def is_in_public_category(content, public_category):
    if public_category is None:
        return False
    spaces = get_spaces_subtree(public_category.id)
    spaces.add(public_category)
    for space in spaces:
        if len(ContentSpace.objects.filter(space=space, content=content)) > 0:
            return True
    return False

def get_contents(space, is_trash=False, order_by='-modified_date'):
    contents = Content.objects.filter(spaces=str(space.id), is_deleted=is_trash).order_by(order_by)
    return contents

def get_spaces_path_for_corporate_content(content, space_filter):
    ''' Gets the spaces path for a given content.
    Path is a list of Space object in order from second level
    down to the space that the content is associated with.

    space_filter is a lambda used to filter the spaces, ie. to filter
    public spaces only pass 'lambda space: space.is_public()'
    '''
    space = None
    spaces = []
    for cs in content.contentspace_set.all():
        if space_filter(cs.space):
            space = cs.space
            break

    while space and not space.is_top_level():
        if space.parent.is_second_level():
            spaces.append(space)
            space.project = space
        space = space.parent
    spaces.reverse()

    return spaces

def get_division_for_space(space):
    while space and not space.is_second_level():
        space = space.parent
    return space

def get_contents_from_company(company, content_filter):
    filtered_contents = []
    contents = Content.objects.filter(spaces=str(company.id))
    for content in contents:
        if(content_filter(content)):
            filtered_contents.append(content)
    return filtered_contents

def get_publication_for_space(space):
    if not space.parent:
        return None
    if space.parent.is_second_level():
        return space
    while not space.parent.is_second_level():
        space = space.parent
    return space

def check_manage_access_rights(space_access_set):
    has_manage_access_rights = False
    for sa in space_access_set:
        if (not sa.space.is_private()) and sa.has_permission("SPACE_ACCESS_MANAGE"):
            has_manage_access_rights = True
    return has_manage_access_rights

def get_space_accesses_to_projects(space_access_set):
    space_accesses = []
    for sa in space_access_set:
        if not sa.space.is_corporate():
            continue
        if sa.space.is_company():
            continue
        space_accesses.append(sa)
    return space_accesses
