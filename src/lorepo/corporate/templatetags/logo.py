from django.template.defaultfilters import register
from src.lorepo.corporate.models import CorporateLogo


@register.inclusion_tag('corporate/logo.html')
def get_logo(user):
    logo = None
    corporate_logo_list = CorporateLogo.objects.filter(space=user.company)
    if len(corporate_logo_list) > 0:
        logo = corporate_logo_list[0].logo
    return {'logo': logo }


@register.filter
def has_logo(user):
    corporate_logo_list = CorporateLogo.objects.filter(space=user.company)
    if len(corporate_logo_list) > 0:
        return True
    return False
