from django import template
from lorepo.spaces.util import load_kids

register = template.Library()

@register.inclusion_tag('localization/localization_project.html')
def localization_project(project, request):
    show = False
    load_kids([project], False)
    spaces = project.loaded_kids
    if spaces:
        show = True
    return { 'spaces' : spaces, 'request' : request, 'show' : show , 'project' : project}