import requests
import libraries.utility.cacheproxy as cache


def fetch(url, timeout=30, cache_time=None, max_retries=3):
    content = None
    if cache_time is not None:
        content = cache.get('requests:fetch:%s' % (url))

    if not content:
        retry = 0
        while retry < max_retries:
            try:
                response = requests.get(url, timeout=timeout)
                retry = max_retries  # Exit loop if successful
            except requests.exceptions.RequestException as e:
                retry += 1
                if retry == max_retries:
                    raise e

        if response.status_code == 200 and len(response.content) > 0:
            content = response.content
            if cache_time is not None:
                cache.set('requests:fetch:%s' % (url), content, cache_time)
        else:
            content = None

    return content


def fetch_nowait(url):
    # Requests does not have an async counterpart directly, but we can simulate async behavior with threading or asyncio.
    import threading
    def fetch_async():
        try:
            requests.get(url)
        except requests.exceptions.RequestException:
            pass  # Handle exception if needed

    # Use threading to make the request "non-blocking" (asynchronously in a separate thread)
    thread = threading.Thread(target=fetch_async)
    thread.start()
