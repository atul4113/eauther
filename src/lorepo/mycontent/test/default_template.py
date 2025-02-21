from django.test.client import Client
from libraries.utility.noseplugins import FormattedOutputTestCase,\
    QueueTestCase
from lorepo.mycontent.models import Content, SpaceTemplate
from libraries.utility.test_assertions import the
from xml.dom import minidom

class DefaultTemplateTests(QueueTestCase):
    fixtures = ['actions.json']

    def setUp(self):
        super(DefaultTemplateTests, self).setUp()
        self.client = Client()
        self.client.login(username='test', password='test')

    def tearDown(self):
        super(DefaultTemplateTests, self).tearDown()
        self.client.logout()

    def test_create_content_with_template(self):
        # Create brand new content which will be a default template
        self.client.post('/mycontent/addcontent', { "title" : "Present Perfect", "tags" : "english,perfect", "description" : "present perfect"})
        last_inserted = Content.objects.latest('modified_date')
        self.client.get('/mycontent/%s/maketemplate' % (last_inserted.id))
        self.client.get('/mycontent/%s/makepublic' % (last_inserted.id))
        default_template = Content.objects.latest('modified_date')

        # Make the new content a default template
        space_template = SpaceTemplate(space=None, template=default_template)
        space_template.save()

        # Create a new content using the template
        self.client.post('/mycontent/addcontent', { "title" : "Present Perfect", "tags" : "english,perfect", "description" : "present perfect"})
        last_inserted = Content.objects.latest('modified_date')

        the(last_inserted.file).does_not_equal(default_template.file)

        default_template_contents = minidom.parseString(default_template.file.contents)
        last_inserted_contents = minidom.parseString(last_inserted.file.contents)

        the(last_inserted_contents.getElementsByTagName('page')).length_is(1)

        default_template_first_page = default_template_contents.getElementsByTagName('page')[0]
        last_inserted_first_page = last_inserted_contents.getElementsByTagName('page')[0]

        the(default_template_first_page.getAttribute('href')).does_not_equal(last_inserted_first_page.getAttribute('href'))
        
class IndependentCopyOfTheOriginalTests(FormattedOutputTestCase):
    fixtures = ['independent_copy.json']
    
    def setUp(self):
        super(IndependentCopyOfTheOriginalTests, self).setUp()
        self.client = Client()
        self.client.login(username='kgebert', password='kgebert1')

    def tearDown(self):
        super(IndependentCopyOfTheOriginalTests, self).tearDown()
        self.client.logout()
        
    def test_header_hrefs_in_content_and_template(self):
        self.client.post('/mycontent/addcontent/1259', {'title' : 'test123'})
        content = Content.objects.latest('created_date')
        template = Content.objects.get(pk=1340)
        
        content_xml = minidom.parseString(content.file.contents)
        template_xml = minidom.parseString(template.file.contents)
        
        content_header_element = [page for page in content_xml.getElementsByTagName('page') if page.getAttribute('name') == 'header'][0]
        template_header_element = [page for page in template_xml.getElementsByTagName('page') if page.getAttribute('name') == 'header'][0]
        
        self.assertNotEqual(template_header_element.getAttribute('href'), content_header_element.getAttribute('href'))
        
    def test_footer_hrefs_in_content_and_template(self):
        self.client.post('/mycontent/addcontent/1259', {'title' : 'test123'})
        content = Content.objects.latest('created_date')
        template = Content.objects.get(pk=1340)
        
        content_xml = minidom.parseString(content.file.contents)
        template_xml = minidom.parseString(template.file.contents)
        
        content_footer_element = [page for page in content_xml.getElementsByTagName('page') if page.getAttribute('name') == 'footer'][0]
        template_footer_element = [page for page in template_xml.getElementsByTagName('page') if page.getAttribute('name') == 'footer'][0]
        self.assertNotEqual(template_footer_element.getAttribute('href'), content_footer_element.getAttribute('href'))