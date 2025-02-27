from django.urls import path
from src.lorepo.corporate.views import SpaceArchiveJobView, SpaceRetrieveJobView, SpaceDeleteJobView, DeleteSpaceAsyncView, \
    ArchiveSpaceAsyncView, RetrieveSpaceAsyncView, more_projects_dashboard, view, view_addon, upload, company_public_spaces, \
    add_public_space, company_divisions, delete_division, remove_contents_from_division, rename_division, add_division, \
    admin_panel, division_panel, public_space, list_presentations, trash, delete, metadata, publish, create_new_content_version, \
    addon_metadata, create_company, create_trial_account, create_company_owner, make_public, fixdb_public_content, fixdb_projects, \
    fixdb_public_content_metadata, fixdb_public_content_metadata_task, projectControl, ajax_subprojects, addSubproject, project_list, \
    change_template, flush_user_cache, copy_to_account, toggle_include_contents_in_editor, bug_track_add_form, get_publications_for_project_json, \
    select_unit, clear_news_cache, no_space_info, set_demo_sample_lessons
from src.lorepo.mycontent.fix_ssl import SslReportView
from src.lorepo.spaces.models import SpaceType
from src.lorepo.spaces.views import addSpace, renameProject, rank
from src.lorepo.corporate.api import get_news

urlpatterns = [
    # Corporate views
    path('', more_projects_dashboard),
    path('<int:space_id>/', more_projects_dashboard),
    path('view/<int:content_id>/', view),
    path('view_addon/<int:addon_id>/', view_addon),
    path('upload/', upload),
    path('publicspaces', company_public_spaces, name='public_space_control'),
    path('add_public', add_public_space),
    path('divisions', company_divisions),
    path('<int:space_id>/delete_space', delete_division),
    path('remove_contents/<int:space_id>', remove_contents_from_division),
    path('<int:space_id>/rename_space', rename_division),
    path('add/<int:space_id>', add_division),
    path('admin', admin_panel),
    path('divisionadmin', division_panel),
    path('public/<int:space_id>', public_space),
    path('list/<int:space_id>', list_presentations),
    path('list/<int:space_id>/trash', trash),
    path('<int:content_id>/delete', delete),
    path('<int:content_id>/metadata', metadata),
    path('<int:content_id>/publish', publish),
    path('<int:content_id>/newVersion', create_new_content_version),
    path('<int:addon_id>/addon_metadata', addon_metadata),
    path('create_company', create_company),
    path('create_trial_account', create_trial_account),
    path('create_company_owner', create_company_owner),
    path('<int:content_id>/makepublic', make_public),
    path('fixdb_public_content', fixdb_public_content),
    path('fixdb_projects', fixdb_projects),
    path('fixdb_public_content_metadata', fixdb_public_content_metadata),
    path('fixdb_public_content_metadata_task/<int:portion>', fixdb_public_content_metadata_task),
    path('<int:space_id>/subproject', projectControl, name='project_control'),
    path('<int:space_id>/ajax_subprojects', ajax_subprojects),
    path('<int:space_id>/add_subproject', addSubproject),
    path('projects/<int:space_id>', project_list, name='corporate_projects'),
    path('change_template', change_template),
    path('drop_cache/<int:company_id>', flush_user_cache),
    path('copy_to_account/<int:content_id>', copy_to_account),
    path('<int:project_id>/toggle_include', toggle_include_contents_in_editor),
    path('bug_track_add_form', bug_track_add_form),
    path('get_publications_for_project_json', get_publications_for_project_json),
    path('select_unit/<int:content_id>/<int:publication_id>', select_unit),
    path('clear_news_cache', clear_news_cache),
    path('no_space_info', no_space_info),
    path('set_demo_sample_lessons', set_demo_sample_lessons),
    path('ssl_report/<int:space_id>_<int:file_id>', SslReportView.as_view(space_type=SpaceType.CORPORATE)),

    # Publication Views
    path('archive/<int:space_id>', SpaceArchiveJobView.as_view()),
    path('retrieve/<int:space_id>', SpaceRetrieveJobView.as_view()),
    path('delete/<int:space_id>', SpaceDeleteJobView.as_view()),
    path('delete_project_async/<int:job_id>', DeleteSpaceAsyncView.as_view()),
    path('archive_project_async/<int:job_id>', ArchiveSpaceAsyncView.as_view()),
    path('retrieve_project_async/<int:job_id>', RetrieveSpaceAsyncView.as_view()),

    # Spaces Views
    path('projects/add/<int:space_id>', addSpace),
    path('projects/<int:space_id>/rename_project', renameProject, {'template': 'corporate/rename_project.html'}),
    path('projects/<int:space_id>/rename_section', renameProject, {'template': 'corporate/rename_section.html'}),
    path('projects/<int:space_id>/section_rank', rank, {'template': 'corporate/section_rank.html'}),

    # API Views
    path('api/news', get_news),
]
