from django.conf.urls import url
from django.utils.decorators import method_decorator
from lorepo.permission.decorators import has_space_access
from lorepo.permission.models import Permission
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import views
from django.template.defaultfilters import truncatewords
import feedparser
from django.utils import html
import libraries.utility.cacheproxy as cache
import datetime
from django.template.defaultfilters import date as django_date


class NewsView(views.APIView):
    permission_classes = (IsAuthenticated, )


    @method_decorator(has_space_access(Permission.CONTENT_VIEW))
    def get(self, *args, **kwargs):
        try:
            feed = feedparser.parse('http://multiplatformeditor.wordpress.com/feed/')
            news = feed.entries[0:5]
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

        # return HttpResponse(json.dumps(news_json_data), content_type='application/json')
        return Response(news_json_data)



urlpatterns = [
    url(r'^$', NewsView.as_view(), name='news'),
    ]