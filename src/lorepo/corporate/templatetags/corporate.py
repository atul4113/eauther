import re
import src.libraries.utility.cacheproxy as cache
from django import template
from src.lorepo.corporate.models import PROJECT_ADMIN_PERMISSIONS
from src.lorepo.mycontent.models import ContentType
from src.lorepo.spaces.models import UserSpacePermissions
from src.lorepo.spaces.util import  load_kids

register = template.Library()

CORPORATE_LIST = re.compile('^/corporate/list/\d+(/trash){0,1}$')
CORPORATE_VIEW = re.compile('^/corporate/view/d+')
ADD_CONTENT = re.compile('^/mycontent/addcontent')
RENAME_SPACE = re.compile('^/corporate/\d+/rename_space')
CORPORATE_SUBPROJECT = re.compile('^/corporate/\d+/(?!subproject)')
MYCONTENT = re.compile('^/mycontent/\d+/(?!trash)')

@register.inclusion_tag("simple_menu_item.html")
def corporate_dashboard(request, name, path, classes):
    if request.user.is_authenticated():
        if request.user.company is not None:
            name = request.user.company.title
            path = '/corporate/'
            if re.search('^/corporate/{0,1}$', request.path) or re.search('^/corporate/\d+$', request.path) :
                classes += ' selected'
    else:
        if re.search('^/$', request.path):
            classes += ' selected'
    return {'name': name, 'path' : path, 'classes' : classes}

@register.inclusion_tag("spaces_menu.html", takes_context=True)
def corporate_subspaces_menu(context):
    request = context['request']
    s = list(request.user.divisions.values())
    s = sorted(s, key=lambda space: space.title)
    s = [space for space in s if not space.is_top_level()]
    return {'spaces': s}
@register.inclusion_tag("spaces_menu_links.html")
def corporate_subspaces_menu_links(request):
    s = list(request.user.divisions.values())
    s = sorted(list(s), key=lambda space: space.title)
    s = [s for s in s if not s.is_top_level()]
    return {'spaces' : s}

@register.inclusion_tag('corporate/children.html')
def corporate_spaces_list(spaces, selected_space):
    spaces = sorted(spaces, key=lambda space: space.rank)
    return {'spaces': spaces, 'selected_space' : selected_space }

#local

# register = template.Library()


@register.filter
def is_any_division_admin(user, manual_flag=None):
    # If manual_flag is provided, return it directly
    if manual_flag is not None:
        return manual_flag

    # Existing logic
    if user.is_superuser:
        return True

    is_he = cache.get(f"is_any_division_admin_{user.id}")
    if is_he is None:
        usp = UserSpacePermissions.get_cached_usp_for_user(user)
        for division in list(user.divisions.values()):
            perms = usp.get_permissions_for_space(division.id)
            if perms:
                for permission in PROJECT_ADMIN_PERMISSIONS:
                    if permission in perms:
                        cache.set(f"is_any_division_admin_{user.id}", True)
                        return True
            for project in division.kids.all():
                perms = usp.get_permissions_for_space(project.id)
                if perms:
                    for permission in PROJECT_ADMIN_PERMISSIONS:
                        if permission in perms:
                            cache.set(f"is_any_division_admin_{user.id}", True)
                            return True
    else:
        return is_he

    cache.set(f"is_any_division_admin_{user.id}", False)
    return False

#development
# @register.filter
# def is_any_division_admin(user):
#     if user.is_superuser:
#         return True
#     is_he = cache.get("is_any_division_admin_%s"%(user.id))
#     if is_he is None:
#         usp = UserSpacePermissions.get_cached_usp_for_user(user)
#         for division in list(user.divisions.values()):
#             perms = usp.get_permissions_for_space(division.id)
#             if not perms:
#                 pass
#             else:
#                 for permission in PROJECT_ADMIN_PERMISSIONS:
#                     if permission in perms:
#                         cache.set("is_any_division_admin_%s"%(user.id), True)
#                         return True
#             for project in division.kids.all():
#                 perms = usp.get_permissions_for_space(project.id)
#                 if not perms:
#                     pass
#                 else:
#                     for permission in PROJECT_ADMIN_PERMISSIONS:
#                         if permission in perms:
#                             cache.set("is_any_division_admin_%s"%(user.id), True)
#                             return True
#     else:
#         return is_he
#     cache.set("is_any_division_admin_%s"%(user.id), False)
#     return False

@register.inclusion_tag('corporate/projects_list.html')
def children_tag_projects_list(spaces, selected_space, is_trash, root):
    spaces = sorted(spaces, key=lambda space: space.rank)
    return {'spaces': spaces, 'selected_space' : selected_space, 'is_trash' : is_trash, 'root' : root}

@register.inclusion_tag('corporate/children_corporate.html')
def children_tag_corporate(spaces, project_id, token_key, token):
    spaces = sorted(spaces, key=lambda space: space.rank)
    return {'spaces': spaces, 'project_id' : project_id, 'token_key': token_key, 'token': token}

@register.inclusion_tag('corporate/copy_spaces.html')
def copy_spaces(division, request, content_id):
    show = False
    load_kids([division], False)
    spaces = division.loaded_kids
    if spaces:
        show = True

    return { 'spaces' : sorted(list(spaces), key=lambda space: space.title), 'content_id' : content_id, 'request' : request, 'show' : show , 'division' : division}

@register.inclusion_tag('corporate/template_for_content.html')
def get_template_for_content(content):
    template = None
    content_self_is_template = False
    if content and content.content_type != ContentType.ADDON:
        template = content.get_template()
        content_self_is_template = True if content.content_type == ContentType.TEMPLATE else False
    return { 'template' : template, 'content_self_is_template' : content_self_is_template }

@register.inclusion_tag('corporate/space_radioboxes.html')
def render_radioboxes(spaces, currentlySelected, is_first, is_unit_selected = 0):
    load_kids(spaces, False)
    if int(is_first):
        for space in spaces:
            if currentlySelected.pk == space.pk:
                is_unit_selected = 1
    return { 'spaces': spaces, 
            'is_first' : is_first, 
            'currentlySelected' : currentlySelected, 
            'is_unit_selected' : is_unit_selected }


@register.inclusion_tag('corporate/view_actions_menu.html')
def make_corporate_view_actions_menu(sub_menus):
    return {'sub_menus' : sub_menus }
