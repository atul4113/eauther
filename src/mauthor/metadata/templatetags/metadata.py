from django.template.defaultfilters import register
from src.mauthor.metadata.models import DefinitionType

@register.inclusion_tag('metadata/render_definition_form.html')
def render_definition_form(definition, language_bidi , suffix=''):
    return {'definition' : definition, 'language_bidi': language_bidi, 'DefinitionType' : DefinitionType, 'suffix' : suffix}

@register.inclusion_tag('metadata/render_select_tag.html')
def render_select_tag(definition, suffix=''):
    selected = None
    if hasattr(definition, 'entered_value'):
        selected = definition.entered_value
    if hasattr(definition, 'unused'):
        unused = True
    else:
        unused = False
    values = definition.value.split(',')
    return {'values' : values, 'selected' : selected, 'suffix' : suffix, 'unused': unused}