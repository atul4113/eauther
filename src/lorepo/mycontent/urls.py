from django.conf.urls import patterns
from lorepo.mycontent.fix_ssl import SslReportView
from lorepo.spaces.models import SpaceType
from .views import ConfirmSelfEditing, ConfirmEditing, ConfirmSelfEditingAddon

urlpatterns = patterns('lorepo.mycontent.views',
    (r'^$', 'index'),
    (r'^(?P<space_id>\d+)/trash/{0,1}$', 'trash'),
    (r'^(?P<space_id>\d+)$', 'index'),
    (r'^addcontent$', 'add_content'),
    (r'^addcontent/(?P<space_id>\d+)$', 'add_content'),
    (r'^(?P<content_id>\d+)/editor$', 'editor'),
    (r'^view/(?P<content_id>\d+)$', 'preview'),
    (r'^(?P<content_id>\d+)/metadata$', 'metadata'),
    (r'^(?P<content_id>\d+)/pagemetadata$', 'pagemetadata'),
    (r'^copy/(?P<content_id>\d+)/(?P<space_id>\d+)$', 'copy'),
    (r'^copy/(?P<content_id>\d+)$', 'copy'),
    (r'^copy_public_lesson/(?P<content_id>\d+)$', 'copy_public_lesson'),
    (r'^(?P<content_id>\d+)/changeicon$', 'changeIcon'),
    (r'^(?P<content_id>\d+)/makepublic$', 'make_public'),
    (r'^(?P<content_id>\d+)/make_globally_public$', 'make_globally_public'),
    (r'^(?P<content_id>\d+)/updatepublic/(?P<version>\d+)$', 'update_public'),
    (r'^(?P<content_id>\d+)/maketemplate$', 'make_template'),
    (r'^(?P<content_id>\d+)/delete$', 'delete'),
    (r'^(?P<content_id>\d+)/history$', 'show_history'),
    #(r'^(?P<content_id>\d+)/fix_ssl$', 'fix_ssl'),
    (r'^check_ssl_space/(?P<space_id>\d+)$', 'check_ssl_space'),
    (r'^check_ssl_space_backend/(?P<space_id>\d+)$', 'check_ssl_space_backend'),
    (r'^ssl_report/(?P<space_id>\d+)_(?P<file_id>\d+)$', SslReportView.as_view(space_type=SpaceType.PRIVATE)),
    (r'^check_ssl_corporate_spaces$', 'check_ssl_corporate_spaces'),
    (r'^check_ssl_private_spaces$', 'check_ssl_private_spaces'),
    (r'^(?P<content_id>\d+)/setversion/(?P<version_id>\d+)$', 'set_version'),
    (r'^addon$', 'addon'),
    (r'^addon/(?P<space_id>\d+)$', 'addon'),
    (r'^view_addon/(?P<addon_id>\d+)$', 'view_addon'),
    (r'^(?P<addon_id>\d+)/addonmetadata$', 'addon_metadata'),
    (r'^(?P<addon_id>\d+)/editaddon$', 'edit_addon'),
    (r'^(?P<addon_id>\w+)/getaddon$', 'get_addon'),
    (r'^(?P<content_id>\d+)/change_addon_icon$', 'changeAddonIcon'),
    (r'^make_public/(?P<content_id>\d+)$', 'make_public'),
    (r'^goToPage$', 'go_to_page'),
    (r'^(?P<content_id>\d+)/exit_editor$', 'exit_editor'),
    (r'^updatetemplate/(?P<content_id>\d+)$', 'update_template'),
    (r'^update_assets/(?P<content_id>\d+)$', 'update_assets'),
    (r'^update_assets_async/(?P<content_id>\d+)/(?P<user_id>\d+)$', 'update_assets_async'),
    (r'^extract/(?P<content_id>\d+)$', 'extract_pages'),
    (r'^extract/(?P<content_id>\d+)/(?P<space_id>\d+)$', 'extract_pages'),
    (r'^(?P<content_id>\d+)/removeversion/(?P<version_id>\d+)/(?P<old_version>\d+)$', 'remove_version'),
    (r'^fix_removed_version/(?P<content_id>\d+)$', 'fix_removed_version'),
    (r'^(?P<content_id>\d+)/cancelediting$', 'cancel_editing'),
    (r'^fix_being_edited$', 'fix_being_edited'),
    (r'^broken_templates_trigger$', 'broken_templates_trigger'),
    (r'^broken_templates/(?P<space_id>\d+)/(?P<user_id>\d+)$', 'broken_templates'),
    (r'^save_favourite_modules$', 'save_favourite_modules'),
    (r'^save_should_render$', 'save_should_render'),
    (r'^(?P<content_id>\d+)/confirm_self_editing$', ConfirmSelfEditing.as_view()),
    (r'^(?P<content_id>\d+)/confirm_self_editing_addon$', ConfirmSelfEditingAddon.as_view()),
    (r'^(?P<content_id>\d+)/confirm_editing$', ConfirmEditing.as_view()),
)

