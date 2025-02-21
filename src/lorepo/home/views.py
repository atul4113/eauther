import logging

from django.http import HttpResponse

from libraries.utility.decorators import backend
from lorepo.global_settings.models import GlobalSettings
from lorepo.home.models import WebSite


@backend
def unpack_website(request, website_id):
    wb = WebSite.objects.get(pk=website_id)
    if wb.status == WebSite.Status.IN_PROGRESS:
        wb.cleanup()
        wb.extract()

        key = '{}_{}'.format(wb.language.lang_key, wb.version)
        global_settings = GlobalSettings.load()
        global_settings.referrers[key] = wb.url
        global_settings.save()
    else:
        logging.error('Tried to unpack a website but status is %s.' % wb.status)
    return HttpResponse('OK')
