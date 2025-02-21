from google.appengine.api import urlfetch
import libraries.utility.cacheproxy as cache

def fetch(url, timeout=30, cache_time=None, max_retries=3):
    content = None
    if cache_time is not None:
        content = cache.get('urlfetch:fetch:%s' % (url))
    if not content:
        retry = 0
        while retry < max_retries:
            try:
                response = urlfetch.fetch(url, deadline=timeout)
                retry = max_retries
            except Exception as e:
                retry = retry + 1
                if retry == max_retries:
                    raise e

        if response.status_code == 200 and len(response.content) > 0:
            content = response.content
            if cache_time is not None:
                cache.set('urlfetch:fetch:%s' % (url), content, cache_time)
        else:
            content = None
    return content

def fetch_nowait(url):
    rpc = urlfetch.create_rpc()
    urlfetch.make_fetch_call(rpc, url)
