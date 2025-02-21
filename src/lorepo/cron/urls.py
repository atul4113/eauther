from django.conf.urls import patterns

urlpatterns = patterns('lorepo.cron.views',
    (r'^keepalive$', 'keepalive'),
    (r'^delete_old_courses$', 'delete_old_courses'),
    (r'^delete_old_courses_cron$', 'delete_old_courses_cron'),
    (r'^delete_old_courses_async$', 'delete_old_courses_async'),
    (r'^lock_companies$', 'lock_companies'),
    (r'^lock_companies_cron$', 'lock_companies_cron'),
    (r'^lock_companies_async$', 'lock_companies_async'),
    (r'^is_more_users_in_company$', 'is_more_users_in_company'),
    (r'^is_more_users_in_company_cron$', 'is_more_users_in_company_cron'),
    (r'^is_more_users_in_company_async$', 'is_more_users_in_company_async'),
)

