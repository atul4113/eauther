import logging
import re

SKIPPED_URLS = re.compile('(^/accounts/login)|(^/file/serve/)|(.*file/upload.*)|(.*file_secure/upload.*)|(/_ah.*)')
LOGGING_URL = re.compile('(^/accounts/login)')

class LoggingMiddleware(object):
    def process_request(self, request):
        if not SKIPPED_URLS.search(request.path):
            if request.method == 'GET':
                logging.debug("User: %s, GET Request: %s", request.user, request.GET)
            elif request.method == 'POST':
                logging.debug("User: %s, POST Request: %s", request.user, request.POST)
                logging.debug("POST payload size: " + str(request.META.get('CONTENT_LENGTH')))
            else:
                logging.debug("User: %s, %s Request: %s", request.user, request.method, request.REQUEST)

        if LOGGING_URL.search(request.path) and "username" in request.POST:
            logging.debug("Loging-in user: %s", request.POST.get('username'))

        return None