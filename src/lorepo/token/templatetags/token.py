from django import template
from lorepo.token.decorators import get_form_token

register = template.Library()


@register.inclusion_tag('token/form_token.html', takes_context=True)
def form_token(context, key):
    request = context['request']
    token = get_form_token(request.user, key)

    return {
        'key': key,
        'token': token if token else ''
    }