import libraries.utility.cacheproxy as cache

def flush_addons_cache(sender, **kwargs):
    company_id = kwargs['company_id']
    cache.delete('addons_for_%s' % company_id)

def flush_templates_cache(sender, **kwargs):
    company_id = kwargs['company_id']
    cache.delete('templates_for_%s' % company_id)

