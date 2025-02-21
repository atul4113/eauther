import libraries.utility.timing as timing
from django.template.defaultfilters import register
from libraries.utility.environment import get_app_version
from django.core.urlresolvers import resolve, Resolver404
import re

@register.filter
def timing_start(label):
    timing.start(label)
    return ''

@register.filter
def timing_end(label):
    timing.end(label)
    return ''

@register.simple_tag
def timing_stats():
    return '<pre>%s</pre>' % timing.get_times()

@register.simple_tag
def get_app_version_tag():
    return get_app_version()

@register.inclusion_tag('utility/sql_log_queries.html')
def sql_log_queries(sql_queries):
    return {'sql_queries' : sql_queries}

@register.filter
def remove_request_token(url):
    return re.sub('\_TOKEN\=.{5}', '', url)


def is_active(url, urls):
    try:
        urlconf = resolve(url)
        return hasattr(urlconf, 'url_name') and urlconf.url_name in urls
    except Resolver404:
        return False


@register.filter
def is_home_active(url):
    urls = ['home']
    return is_active(url, urls)


@register.filter
def is_dashboard_active(url):
    urls = ['dashboard']
    return is_active(url, urls)


@register.filter
def is_my_lessons_active(url):
    urls = ['my_lessons']
    return is_active(url, urls)


@register.filter
def is_projects_active(url):
    urls = ['projects']
    return is_active(url, urls)


@register.filter
def is_support_active(url):
    urls = ['support']
    return is_active(url, urls)


@register.filter
def is_help_active(url):
    urls = ['help']
    return is_active(url, urls)