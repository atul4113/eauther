import logging

from django.http.response import HttpResponse

from libraries.utility.decorators import backend


@backend
def object_method(request, module, model, method, id):
    module = __import__(module, fromlist=model)
    cls = getattr(module, model)
    obj = cls.objects.get(pk=id)
    object_method = getattr(obj, method)
    if obj.retry_exceptions is not None:
        try:
            object_method()
        except obj.retry_exceptions as e:
            logging.error('Retry exception:')
            logging.error(e)
            return HttpResponse('', status=409)
    else:
        object_method()

    return HttpResponse()