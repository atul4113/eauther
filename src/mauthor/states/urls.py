from django.urls import path
from mauthor.states.views import ProjectStates, change_state, change_to_ready, list_sets, update_rank, update_percentage, delete_state, delete_set, rename_state, show_kanban

urlpatterns = [
    # View URLs
    path('change/<int:content_id>/<int:state_id>/', change_state),
    path('change_to_ready/<int:content_id>/<int:state_id>/', change_to_ready),
    path('project/<int:project_id>/', ProjectStates.as_view()),
    path('sets/', list_sets),
    path('sets/<int:set_id>/', list_sets),
    path('update_rank/<int:state_id>/<int:new_rank>/', update_rank),
    path('update_percentage/<int:state_id>/<int:percentage>/', update_percentage),
    path('delete/<int:state_id>/', delete_state),
    path('delete_set/<int:set_id>/', delete_set),
    path('rename/<int:state_id>/', rename_state),
    path('show_kanban/<int:project_id>/', show_kanban),
]
