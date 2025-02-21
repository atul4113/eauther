from django.template.defaultfilters import register

@register.filter
def all_empty(pages):
    for page in pages:
        if len(page.narrations) > 0:
            return False
    return True