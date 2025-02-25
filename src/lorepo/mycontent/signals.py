import django.dispatch
import libraries.utility.cacheproxy as cache


content_updated = django.dispatch.Signal()
addon_published = django.dispatch.Signal()
addon_deleted = django.dispatch.Signal()
template_updated = django.dispatch.Signal()
metadata_updated = django.dispatch.Signal()
metadata_updated_async = django.dispatch.Signal()



def flush_content_cache(sender, **kwargs):
    content_id = kwargs['content_id']
    cache.delete('content_template_%s' % content_id)

