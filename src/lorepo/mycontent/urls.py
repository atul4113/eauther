from django.urls import path, re_path
from lorepo.mycontent.fix_ssl import SslReportView
from lorepo.spaces.models import SpaceType
from .views import ConfirmSelfEditing, ConfirmEditing, ConfirmSelfEditingAddon
from .views import index, trash, add_content, editor, preview, metadata, pagemetadata, copy, copy_public_lesson, \
    changeIcon, make_public, make_globally_public, update_public, make_template, delete, show_history, \
    check_ssl_space, check_ssl_space_backend, check_ssl_corporate_spaces, check_ssl_private_spaces, \
    set_version, addon, view_addon, addon_metadata, edit_addon, get_addon, changeAddonIcon, go_to_page, exit_editor, \
    update_template, update_assets, update_assets_async, extract_pages, remove_version, fix_removed_version, \
    cancel_editing, fix_being_edited, broken_templates_trigger, broken_templates, save_favourite_modules, \
    save_should_render

urlpatterns = [
    path('', index, name='index'),
    re_path(r'^(?P<space_id>\d+)/trash/{0,1}$', trash, name='trash'),
    re_path(r'^(?P<space_id>\d+)$', index, name='space_index'),
    path('addcontent', add_content, name='add_content'),
    path('addcontent/<int:space_id>', add_content, name='add_content_with_space'),
    re_path(r'^(?P<content_id>\d+)/editor$', editor, name='editor'),
    re_path(r'^view/(?P<content_id>\d+)$', preview, name='preview'),
    re_path(r'^(?P<content_id>\d+)/metadata$', metadata, name='metadata'),
    re_path(r'^(?P<content_id>\d+)/pagemetadata$', pagemetadata, name='pagemetadata'),
    re_path(r'^copy/(?P<content_id>\d+)/(?P<space_id>\d+)$', copy, name='copy_content_with_space'),
    re_path(r'^copy/(?P<content_id>\d+)$', copy, name='copy_content'),
    re_path(r'^copy_public_lesson/(?P<content_id>\d+)$', copy_public_lesson, name='copy_public_lesson'),
    re_path(r'^(?P<content_id>\d+)/changeicon$', changeIcon, name='change_icon'),
    re_path(r'^(?P<content_id>\d+)/makepublic$', make_public, name='make_public'),
    re_path(r'^(?P<content_id>\d+)/make_globally_public$', make_globally_public, name='make_globally_public'),
    re_path(r'^(?P<content_id>\d+)/updatepublic/(?P<version>\d+)$', update_public, name='update_public'),
    re_path(r'^(?P<content_id>\d+)/maketemplate$', make_template, name='make_template'),
    re_path(r'^(?P<content_id>\d+)/delete$', delete, name='delete'),
    re_path(r'^(?P<content_id>\d+)/history$', show_history, name='show_history'),
    re_path(r'^check_ssl_space/(?P<space_id>\d+)$', check_ssl_space, name='check_ssl_space'),
    re_path(r'^check_ssl_space_backend/(?P<space_id>\d+)$', check_ssl_space_backend, name='check_ssl_space_backend'),
    re_path(r'^ssl_report/(?P<space_id>\d+)_(?P<file_id>\d+)$', SslReportView.as_view(space_type=SpaceType.PRIVATE), name='ssl_report'),
    path('check_ssl_corporate_spaces', check_ssl_corporate_spaces, name='check_ssl_corporate_spaces'),
    path('check_ssl_private_spaces', check_ssl_private_spaces, name='check_ssl_private_spaces'),
    re_path(r'^(?P<content_id>\d+)/setversion/(?P<version_id>\d+)$', set_version, name='set_version'),
    path('addon', addon, name='addon'),
    path('addon/<int:space_id>', addon, name='addon_with_space'),
    re_path(r'^view_addon/(?P<addon_id>\d+)$', view_addon, name='view_addon'),
    re_path(r'^(?P<addon_id>\d+)/addonmetadata$', addon_metadata, name='addon_metadata'),
    re_path(r'^(?P<addon_id>\d+)/editaddon$', edit_addon, name='edit_addon'),
    re_path(r'^(?P<addon_id>\w+)/getaddon$', get_addon, name='get_addon'),
    re_path(r'^(?P<content_id>\d+)/change_addon_icon$', changeAddonIcon, name='change_addon_icon'),
    path('make_public/<int:content_id>', make_public, name='make_public_by_id'),
    path('goToPage', go_to_page, name='go_to_page'),
    re_path(r'^(?P<content_id>\d+)/exit_editor$', exit_editor, name='exit_editor'),
    re_path(r'^updatetemplate/(?P<content_id>\d+)$', update_template, name='update_template'),
    re_path(r'^update_assets/(?P<content_id>\d+)$', update_assets, name='update_assets'),
    re_path(r'^update_assets_async/(?P<content_id>\d+)/(?P<user_id>\d+)$', update_assets_async, name='update_assets_async'),
    re_path(r'^extract/(?P<content_id>\d+)$', extract_pages, name='extract_pages'),
    re_path(r'^extract/(?P<content_id>\d+)/(?P<space_id>\d+)$', extract_pages, name='extract_pages_with_space'),
    re_path(r'^(?P<content_id>\d+)/removeversion/(?P<version_id>\d+)/(?P<old_version>\d+)$', remove_version, name='remove_version'),
    path('fix_removed_version/<int:content_id>', fix_removed_version, name='fix_removed_version'),
    re_path(r'^(?P<content_id>\d+)/cancelediting$', cancel_editing, name='cancel_editing'),
    path('fix_being_edited', fix_being_edited, name='fix_being_edited'),
    path('broken_templates_trigger', broken_templates_trigger, name='broken_templates_trigger'),
    re_path(r'^broken_templates/(?P<space_id>\d+)/(?P<user_id>\d+)$', broken_templates, name='broken_templates'),
    path('save_favourite_modules', save_favourite_modules, name='save_favourite_modules'),
    path('save_should_render', save_should_render, name='save_should_render'),
    re_path(r'^(?P<content_id>\d+)/confirm_self_editing$', ConfirmSelfEditing.as_view(), name='confirm_self_editing'),
    re_path(r'^(?P<content_id>\d+)/confirm_self_editing_addon$', ConfirmSelfEditingAddon.as_view(), name='confirm_self_editing_addon'),
    re_path(r'^(?P<content_id>\d+)/confirm_editing$', ConfirmEditing.as_view(), name='confirm_editing'),
]
