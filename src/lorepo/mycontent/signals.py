import django.dispatch
import libraries.utility.cacheproxy as cache

content_updated = django.dispatch.Signal(providing_args=['content_id', 'content_type'])
addon_published = django.dispatch.Signal(providing_args=['company_id'])
addon_deleted = django.dispatch.Signal(providing_args=['company_id'])
template_updated = django.dispatch.Signal(providing_args=['company_id'])
metadata_updated = django.dispatch.Signal(providing_args=['content_id'])
metadata_updated_async = django.dispatch.Signal(providing_args=['content_id'])


def flush_content_cache(sender, **kwargs):
    content_id = kwargs['content_id']
    cache.delete('content_template_%s' % content_id)

