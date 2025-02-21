import json
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template.defaultfilters import truncatewords
import feedparser
from django.utils import html
import libraries.utility.cacheproxy as cache
import datetime


@login_required
def get_news(_):
    from django.template.defaultfilters import date as django_date

    news = cache.get('home_index:latest_news')

    if not news:
        try:
            feed = feedparser.parse('http://multiplatformeditor.wordpress.com/feed/')
            news = feed.entries[0:3]
            for n in news:
                n.summary = html.strip_tags(n.summary)
                n.published_date = datetime.date(n.published_parsed[0], n.published_parsed[1], n.published_parsed[2])
            cache.set('home_index:latest_news', news, 60 * 60 * 6)
        except:
            pass

    news_json_data = []
    for n in news:
        news_json_data.append({
            'title': n.title,
            'link': n.link,
            'published': django_date(n.published_date),
            'summary': truncatewords(n.summary, 15)
        })

    return HttpResponse(json.dumps(news_json_data), content_type='application/json')