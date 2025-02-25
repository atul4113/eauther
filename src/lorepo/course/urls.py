from django.urls import path, re_path
from .views import (
    courses_list, get_publication_lessons, get_kids, get_space,
    edit_table_of_contents, save_table_of_contents, rename, remove,
    remove_chapter, add_lesson, add_lesson_to_eBook, remove_lessons,
    trigger_export, export, export_structure, export_lesson,
    set_structure_state, save_resources, edit_resources, edit_resources_iframe,
    get_resources
)

urlpatterns = [
    # Regular paths
    re_path(r'^list/(?P<project_id>\d+)/{0,1}$', courses_list, name='courses_list'),
    re_path(r'^get_publication_lessons/(?P<publication_id>\d+)/{0,1}', get_publication_lessons, name='get_publication_lessons'),
    path('get_kids/<int:publication_id>/', get_kids, name='get_kids'),
    path('get_space/<int:course_id>/<int:space_id>/', get_space, name='get_space'),
    re_path(r'^edit_table_of_contents/(?P<course_id>\d+)/(?P<project_id>\d+)/{0,1}', edit_table_of_contents, name='edit_table_of_contents'),
    re_path(r'^save_table_of_contents/(?P<course_id>\d+)/{0,1}', save_table_of_contents, name='save_table_of_contents'),
    path('rename/<int:course_id>/', rename, name='rename'),
    path('remove/<int:course_id>/', remove, name='remove'),
    path('remove_chapter/<int:chapter_id>/<int:course_id>/', remove_chapter, name='remove_chapter'),
    path('add_lesson/<int:chapter_id>/<int:course_id>/', add_lesson, name='add_lesson'),
    path('add_lesson/eBook/<int:course_id>/', add_lesson_to_eBook, name='add_lesson_to_eBook'),
    path('remove_lessons/<int:course_id>/', remove_lessons, name='remove_lessons'),
    path('export/<int:course_id>/', trigger_export, name='trigger_export'),
    re_path(r'^export/(?P<course_id>\d+)/async/(?P<user_id>\d+)/(?P<version>\d+)/(?P<include_player>\d+)$', export, name='export'),
    re_path(r'^export_structure/(?P<course_id>\d+)/(?P<exported_course_id>\d+)/(?P<user_id>\d+)/(?P<version>\d+)$', export_structure, name='export_structure'),
    re_path(r'^export_lesson/(?P<content_id>\d+)/(?P<user_id>\d+)/(?P<exported_course_id>\d+)/(?P<version>\d+)$', export_lesson, name='export_lesson'),
    path('set_structure_state/', set_structure_state, name='set_structure_state'),
    path('save_resources', save_resources, name='save_resources'),
    path('edit_resources/<int:course_id>/<int:content_id>/', edit_resources, name='edit_resources'),
    path('edit_resources_iframe/<int:content_id>/', edit_resources_iframe, name='edit_resources_iframe'),
    path('get_resources/<int:course_id>/<int:content_id>/<int:page_index>/', get_resources, name='get_resources'),
]
