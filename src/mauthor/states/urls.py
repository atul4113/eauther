from django.conf.urls import patterns, url
from mauthor.states.views import ProjectStates

urlpatterns = patterns('mauthor.states.views',
    (r'^change/(?P<content_id>\d+)/(?P<state_id>\d+)$', 'change_state'),
    (r'^change_to_ready/(?P<content_id>\d+)/(?P<state_id>\d+)$', 'change_to_ready'),
    (r'^project/(?P<project_id>\d+)$', ProjectStates.as_view()),
    (r'^sets$', 'list_sets'),
    (r'^sets/(?P<set_id>\d+)$', 'list_sets'),
    (r'^update_rank/(?P<state_id>\d+)/(?P<new_rank>\d+)$', 'update_rank'),
    (r'^update_percentage/(?P<state_id>\d+)/(?P<percentage>\d+)$', 'update_percentage'),
    (r'^delete/(?P<state_id>\d+)$', 'delete_state'),
    (r'^delete_set/(?P<set_id>\d+)$', 'delete_set'),
    (r'^rename/(?P<state_id>\d+)$', 'rename_state'),
    (r'^show_kanban/(?P<project_id>\d+)$', 'show_kanban')
)
