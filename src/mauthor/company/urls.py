from django.conf.urls import patterns

urlpatterns = patterns('mauthor.company.views',
    (r'^list_companies$', 'companies_report'),
    (r'^remove_company_from_test$', 'remove_company_from_test'),
    (r'^details/(?P<space_id>\d+)$', 'details'),
    (r'^edit/(?P<space_id>\d+)$', 'edit_details'),
    (r'^edit_locale/(?P<space_id>\d+)$', 'edit_locale'),
    (r'^lock/(?P<space_id>\d+)$', 'lock'),
    (r'^unlock/(?P<space_id>\d+)$', 'unlock'),
)
