from django.template.defaultfilters import register

@register.inclusion_tag('user/spaces_tree_tag.html')
def spaces_tree_tag(spaces):
    return {'spaces' : spaces}