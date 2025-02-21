from django.conf.urls import patterns, url


urlpatterns = patterns('lorepo.spaces.views',
    (r'^$', 'index'),
    (r'^undelete_project', 'undelete_project'),
    (r'^(?P<space_id>\d+)$', 'index'),
    (r'^add$', 'addSpace'),
    (r'^add/(?P<space_id>\d+)$', 'addSpace'),
    (r'^(?P<space_id>\d+)/rename_space$', 'renameSpace'),
    (r'^(?P<space_id>\d+)/rename_public$', 'renamePublicSpace'),
    (r'^(?P<space_id>\d+)/rename$', '_rename'),
    (r'^(?P<space_id>\d+)/rank$', 'rank'),
    url(r'^public_space$', 'publicSpaceControl', name='public_space_control'),
    (r'^add_public$', 'addPublicSpace'),
    (r'^(?P<space_id>\d+)/subspace$', 'addSubspace'),
    (r'^(?P<space_id>\d+)/delete_public$', 'deletePublicSpace'),
    (r'^(?P<space_id>\d+)/delete_space$', 'deleteSpace'),
    (r'^_make_user_space_permission/(?P<user_id>\d+)/(?P<new_space_id>\d+)','make_user_space_permission_backend'),
    (r'^_make_user_space_permission/(?P<user_id>\d+)','make_user_space_permission_backend'),
    (r'^make_company_user_space_permissions/(?P<company_id>\d+)','make_company_user_space_permissions'),
    (r'^fixdb_make_all_user_space_permissions','fixdb_make_all_user_space_permissions'),
    (r'^make_company_user_space_permissions_backend/(?P<company_id>\d+)','make_company_user_space_permissions_backend'),
    (r'^make_all_companies_space_permissions','make_all_companies_space_permissions'),
)

