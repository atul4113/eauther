from django.conf.urls import patterns


urlpatterns = patterns('lorepo.translations.views',
    (r'^delete_lang_async/(?P<lang_id>\d+)/(?P<user_id>\d+)$', 'delete_lang_async'),
    (r'^add_language_async/(?P<lang_id>\d+)/(?P<user_id>\d+)$', 'add_language_async'),
    (r'^import/2/(?P<space_id>\d+){0,1}$', 'import_translations_step2'),
    (r'^import/4/(?P<space_id>\d+){0,1}$', 'import_translations_step4'),
)