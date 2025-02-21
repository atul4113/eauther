from django.template.defaultfilters import register
from lorepo.spaces.util import get_space_type

@register.inclusion_tag('mycontent/icon.html')
def get_icon(request, content, space_type=None):
    if not space_type:
        space_type = get_space_type(content)
    return { 'request' : request, 'content' : content, 'space_type' : space_type }

@register.filter
def cut_after(string, length):
    if len(string) >= length:
        return string[:length].strip() + "..."
    else:
        return string
    
@register.inclusion_tag('mycontent/publisher.html')
def publisher(content, second_level=None):
    space = None
    for cs in content.contentspace_set.all():
        if cs.space.is_corporate():
            space = cs.space if second_level and cs.space.is_second_level() else cs.space.top_level
    return { 'space' : space, 'content' : content }

@register.inclusion_tag('mycontent/paginator.html')
def paginator(paginator, current_page, extra_params=None, selected=None, objects_name='Lessons'):
    show_last = True if current_page.number + 3 <= paginator.num_pages else False
    show_first = True if current_page.number - 3 >= 1 else False
    
    current_page.page_range = [page for page in paginator.page_range if current_page.number > page - 3 and current_page.number < page + 3]
    if current_page.number - 3 == 1:
        current_page.page_range.remove(2)
    if current_page.number + 3 == paginator.num_pages:
        current_page.page_range.remove(paginator.num_pages - 1)
        
    selected = "&type=" + str(selected) if selected else ''
    
    return { 'paginator' : paginator,
             'extra_params' : extra_params or None,
             'show_last' : show_last,
             'show_first' : show_first,
             'current_page' : current_page,
             'selected' : selected,
             'objects_name' : objects_name
             }
@register.inclusion_tag('mycontent/paginator_form.html')
def paginator_form(path, paginator, current_page, extra_params=None, selected=None):
    selected = "&type=" + str(selected) if selected is not None else ''
    return { 'path' : path,
            'paginator' : paginator,
            'current_page' : current_page,
            'extra_params'  : extra_params,
            'selected'  : selected
            }
    
@register.inclusion_tag('mycontent/dropdown_menu.html')
def make_dropdown_menu(dropdown_title, sub_menus):
    return { 'dropdown_title' : dropdown_title, 'sub_menus' : sub_menus }

@register.inclusion_tag('mycontent/common/sorting.html', takes_context=True)
def sort_by(context):
    return context 