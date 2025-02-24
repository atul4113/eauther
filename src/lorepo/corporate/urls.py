from django.conf.urls import patterns, url
from lorepo.corporate.views import SpaceArchiveJobView, SpaceRetrieveJobView, SpaceDeleteJobView, DeleteSpaceAsyncView, \
    ArchiveSpaceAsyncView, RetrieveSpaceAsyncView
from lorepo.mycontent.fix_ssl import SslReportView
from lorepo.spaces.models import SpaceType

urlpatterns = patterns('lorepo.corporate.views',
    (r'^$', 'more_projects_dashboard'),
    (r'^(?P<space_id>\d+)$', 'more_projects_dashboard'),
    (r'^view/(?P<content_id>\d+)$', 'view'),
    (r'^view_addon/(?P<addon_id>\d+)$', 'view_addon'),
    (r'^upload/{0,1}$', 'upload'),
    url(r'^publicspaces$', 'company_public_spaces', name='public_space_control'),
    (r'^add_public$', 'add_public_space'),
    (r'^divisions$', 'company_divisions'),
    (r'^(?P<space_id>\d+)/delete_space$', 'delete_division'),
    (r'^remove_contents/(?P<space_id>\d+)', 'remove_contents_from_division'),
    (r'^(?P<space_id>\d+)/rename_space$', 'rename_division'),
    (r'^add/(?P<space_id>\d+)$', 'add_division'),
    (r'^admin$', 'admin_panel'),
    (r'^divisionadmin$', 'division_panel'),
    (r'^public/(?P<space_id>\d+)$', 'public_space'),
    (r'^list/(?P<space_id>\d+)$', 'list_presentations'),
    (r'^list/(?P<space_id>\d+)/trash$', 'trash'),
    (r'^(?P<content_id>\d+)/delete$', 'delete'),
    (r'^(?P<content_id>\d+)/metadata$', 'metadata'),
    (r'^(?P<content_id>\d+)/publish$', 'publish'),
    (r'^(?P<content_id>\d+)/newVersion$', 'create_new_content_version'),
    (r'^(?P<addon_id>\d+)/addon_metadata$', 'addon_metadata'),
    (r'^create_company$', 'create_company'),
    (r'^create_trial_account$', 'create_trial_account'),
    (r'^create_company_owner$', 'create_company_owner'),
    (r'^(?P<content_id>\d+)/makepublic$', 'make_public'),
    (r'^fixdb_public_content$', 'fixdb_public_content'),
    (r'^fixdb_projects$', 'fixdb_projects'),
    (r'^fixdb_public_content_metadata$', 'fixdb_public_content_metadata'),
    (r'^fixdb_public_content_metadata_task/(?P<portion>\d+)$', 'fixdb_public_content_metadata_task'),
    url(r'^(?P<space_id>\d+)/subproject$', 'projectControl', name='project_control'),
    url(r'^(?P<space_id>\d+)/ajax_subprojects$', 'ajax_subprojects'),
    (r'^(?P<space_id>\d+)/add_subproject$', 'addSubproject'),
    url(r'^projects/(?P<space_id>\d+)$', 'project_list', name='corporate_projects'),
    (r'^change_template', 'change_template'),
    (r'^drop_cache/(?P<company_id>\d+)$', 'flush_user_cache'),
    (r'^copy_to_account/(?P<content_id>\d+)', 'copy_to_account'),
    (r'^(?P<project_id>\d+)/toggle_include', 'toggle_include_contents_in_editor'),
    (r'^bug_track_add_form$', 'bug_track_add_form'),
    (r'^get_publications_for_project_json$', 'get_publications_for_project_json'),
    (r'^select_unit/(?P<content_id>\d+)/(?P<publication_id>\d+)$', 'select_unit'),
    (r'^clear_news_cache$', 'clear_news_cache'),
    (r'^no_space_info$', 'no_space_info'),
    (r'^set_demo_sample_lessons$', 'set_demo_sample_lessons'),
    (r'^ssl_report/(?P<space_id>\d+)_(?P<file_id>\d+)$', SslReportView.as_view(space_type=SpaceType.CORPORATE)),

    # publication
    (r'^archive/(?P<space_id>\d+)$', SpaceArchiveJobView.as_view()),
    (r'^retrieve/(?P<space_id>\d+)$', SpaceRetrieveJobView.as_view()),
    (r'^delete/(?P<space_id>\d+)$', SpaceDeleteJobView.as_view()),
    (r'^delete_project_async/(?P<job_id>\d+)$', DeleteSpaceAsyncView.as_view()),
    (r'^archive_project_async/(?P<job_id>\d+)$', ArchiveSpaceAsyncView.as_view()),
    (r'^retrieve_project_async/(?P<job_id>\d+)$', RetrieveSpaceAsyncView.as_view()),
)

urlpatterns += patterns('lorepo.spaces.views',
    (r'^projects/add/(?P<space_id>\d+)$', 'addSpace'),
    (r'^projects/(?P<space_id>\d+)/rename_project$', 'renameProject', {'template' : 'corporate/rename_project.html' }),
    (r'^projects/(?P<space_id>\d+)/rename_section$', 'renameProject', {'template' : 'corporate/rename_section.html' }),
    (r'^projects/(?P<space_id>\d+)/section_rank$', 'rank', {'template' : 'corporate/section_rank.html' }),
)

urlpatterns += patterns('lorepo.corporate.api',
    (r'^api/news$', 'get_news'),
)