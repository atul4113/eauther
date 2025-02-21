from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from urllib.parse import urlparse
from libraries.utility.request import get_protocol
from libraries.utility.urlfetch import fetch
import re


CACHE_TIME = 60 * 60 * 2
MAUTHOR_ALIASES = [
    'mauthor\.com',
    'lorepocorporate\.appspot\.com',
    'mauthor-dev\.appspot\.com'
]


def get(request):
    given_url = request.GET.get('url', None)
    if given_url is None:
        raise Http404

    if given_url.startswith(r'//'):
        given_url = "%s:%s" % (get_protocol(request), given_url)

    parsed_given_url = urlparse(given_url)
    actual_url = request.build_absolute_uri("/")
    parsed_actual_url = urlparse(actual_url)

    # URL points to current domain, no need for fetching.
    if (parsed_given_url[1] == parsed_actual_url[1]) and (parsed_given_url[0] == parsed_actual_url[0]):
        return redirect(given_url)

    domains_pattern = r"(" + '|'.join(MAUTHOR_ALIASES) + ")+$"
    if re.search(domains_pattern, parsed_given_url.hostname) is None:
        # Domain from given_url is forbidden
        raise Http404
    elif re.search(domains_pattern, parsed_actual_url.hostname):
        # Domain matches supported aliases, so we don't want to fetch content from same application.
        # In order to support application versioning, we're redirecting to relative path (so it won't hit
        # same-origin policy).
        return redirect(parsed_given_url.path)

    # On development server we're fetching content form mAuthor that wasn't imported (f.i. custom addons).
    content = fetch(given_url, cache_time=CACHE_TIME)
    if not content:
        raise Http404

    response = HttpResponse(content=content)
    response['Cache-Control'] = "private, max-age=" + str(3600*24)

    return response
