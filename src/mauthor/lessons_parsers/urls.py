from django.conf.urls import patterns, url
from mauthor.lessons_parsers.views import ChangePropertiesView, RemoveDescriptorsView

urlpatterns = patterns('mauthor.lessons_parsers.views',
    url(r'^change_properties/(?P<space_id>\d+)$', ChangePropertiesView.as_view()),
    (r'^fix_properties_async/(?P<user_id>\d+)/(?P<space_id>\d+)$', 'fix_properties_async'),
    url(r'^remove_descriptors/(?P<space_id>\d+)$', RemoveDescriptorsView.as_view()),
    (r'^remove_descriptors_async/(?P<user_id>\d+)/(?P<space_id>\d+)$', 'remove_descriptors_async')
)

urlpatterns += patterns('mauthor.lessons_parsers.api',
    (r'^get_properties', 'get_properties'),
    (r'^addon_exist', 'addon_exist')
)
