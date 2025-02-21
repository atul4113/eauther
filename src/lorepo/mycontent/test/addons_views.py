from django.test.client import Client
from lorepo.mycontent.models import Content
from libraries.utility.noseplugins import FormattedOutputTestCase,\
    QueueTestCase

class AddonsViewsTests(QueueTestCase):
    fixtures = ['addons_views.json']

    def setUp(self):
        super(AddonsViewsTests, self).setUp()
        self.client = Client()
        self.client.login(username='kgebert', password='kgebert1')

    def tearDown(self):
        super(AddonsViewsTests, self).tearDown()
        self.client.logout()

    def test_addon(self):
        response = self.client.get('/mycontent/addon/3')
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['form'])
        self.assertTemplateUsed(response, 'mycontent/add_addon.html')
        
    def test_addon_create_properly(self):
        response = self.client.post('/mycontent/addon/3', {'title' : 'test_addon', 'name' : 'test_addon', 'next' : '/corporate/list/1845'})
        self.assertEqual(response.status_code, 302)
        
        addon = Content.objects.latest('created_date')
        self.assertEqual('test_addon', addon.title)
        self.assertEqual('test_addon', addon.name)
        
    def test_addon_create_with_name_already_exists(self):
        response = self.client.post('/mycontent/addon/1845', {'title' : 'karol', 'name' : 'test54321', 'next' : '/corporate/list/1845'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual('Content with name test54321 already exists in database. Please choose different name', response.context['form'].errors['name'][0])

    def test_edit_addon_metadata(self):
        response = self.client.post('/corporate/5848/addon_metadata', {'title' : 'nowy_tytul', 'next' : '/corporate/list/1845'})
        self.assertEqual(response.status_code, 302)
        
        addon = Content.objects.latest('modified_date')
        self.assertEqual('nowy_tytul', addon.title)
        
    def test_delete_addon(self):
        addon_before = Content.objects.get(pk=5848)
        self.assertFalse(addon_before.is_deleted)
        
        response = self.client.get('/corporate/5848/delete?next=/corporate/list/1845')
        self.assertEqual(response.status_code, 302)
        addon_after = Content.objects.get(pk=5848)
        self.assertTrue(addon_after.is_deleted)
        
    
class AddonXMLTags(FormattedOutputTestCase):
    fixtures = ['addon_tags.json']

    def setUp(self):
        self.client = Client()
        self.client.login(username='kgebert', password='kgebert1')

    def tearDown(self):
        self.client.logout()
        
    def test_addon_without_typical_tags(self):
        addon = Content.objects.get(title="addon_without_typical_tags")
        response = self.client.get('/mycontent/view_addon/%(id)s' % {'id' : addon.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['view'], '')
        self.assertEqual(response.context['preview'], '')
        self.assertEqual(response.context['properties'], '')