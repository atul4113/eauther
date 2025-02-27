from django.test.client import Client
from src.libraries.utility.noseplugins import FormattedOutputTestCase
from src.lorepo.mycontent.models import DefaultTemplate, Content

class GloabalTemplateTest(FormattedOutputTestCase):
    fixtures = ['global_template.json']

    def setUp(self):
        super(GloabalTemplateTest, self).setUp()
        self.client = Client()
        self.client.login(username='kgebert', password='kgebert1')
        
    def tearDown(self):
        super(GloabalTemplateTest, self).tearDown()
        
    def test_add_global_template_proper_id(self):
        dt = DefaultTemplate.objects.all()[0]
        self.assertEqual(dt.template.id, 1267)
        
        self.client.post('/user/change_global_template', {'template_id' : 1262})
        
        dt = DefaultTemplate.objects.all()[0]
        self.assertEqual(dt.template.id, 1262)
    
    def test_add_global_template_not_proper_id(self):
        response = self.client.post('/user/change_global_template', {'template_id' : 99699699})
        
        self.assertEqual(response.context['form']['template_id'].errors, ['Template with id 99699699 not found.'])
    
    def test_add_two_global_templates(self):
        dt_count = DefaultTemplate.objects.count()
        self.assertEqual(dt_count, 1)
        
        self.client.post('/user/change_global_template', {'template_id' : 1262})
        
        dt_count = DefaultTemplate.objects.count()
        self.assertEqual(dt_count, 1)
    
    def test_new_content_and_get_template(self):
        response = self.client.post('/mycontent/addcontent/1259', {'title' : 'test'})
        self.assertEqual(302, response.status_code)
        
        latest = Content.objects.latest('created_date')
        self.assertEqual('test', latest.title)
        
        self.assertEqual(1267, latest.get_template().id)