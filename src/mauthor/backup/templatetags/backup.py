from django.template.defaultfilters import register

@register.inclusion_tag('backup/space_checkboxes.html')
def render_checkboxes(spaces):
    return {'spaces': spaces }
