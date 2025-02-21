from django.conf.urls import patterns


urlpatterns = patterns('lorepo.labels.views',
    (r'^$', 'index'),
    (r'^add$', 'addLabel'),
    (r'^(?P<label_id>\d+)/rename$', 'rename'),
)

