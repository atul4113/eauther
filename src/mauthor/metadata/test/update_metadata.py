from libraries.utility.noseplugins import FormattedOutputTestCase
from xmlbuilder import XMLBuilder
from django.contrib.auth.models import User
import datetime
from lorepo.filestorage.models import FileStorage
from lorepo.mycontent.models import Content
from mauthor.metadata.util import update_page_metadata
from mauthor.metadata.models import PageMetadata
from libraries.utility.test_assertions import the

class UpdateMetadataTests(FormattedOutputTestCase):
    fixtures = ['libraries.testing.users.json', 'libraries.testing.mycontent.json']
    
    def setUp(self):
        self.user = User.objects.get(pk=1)
        now = datetime.datetime.now()
        self.file = FileStorage(created_date = now,
                           modified_date = now,
                           content_type = "text/xml",
                           contents = build_content(pages=2),
                           owner = self.user)
        self.file.save()
        self.content = Content.objects.get(pk=1)
        self.content.file = self.file
        self.content.enable_page_metadata = True
        self.content.save()
    
    def tearDown(self):
        pass
    
    def test_page_has_been_added(self):
        self._perform_test_with_number_of_pages(3)
    
    def test_page_has_been_removed(self):
        self._perform_test_with_number_of_pages(1)        
    
    def test_the_same_amount_of_pages(self):
        self._perform_test_with_number_of_pages(2)
    
    def _perform_test_with_number_of_pages(self, pages):
        update_page_metadata(self.content)
        page_metadata = PageMetadata.objects.filter(content=self.content)
        the(page_metadata).length_is(2)
        
        self.content.file.contents = build_content(pages=pages)
        update_page_metadata(self.content)
        page_metadata = PageMetadata.objects.filter(content=self.content)
        the(page_metadata).length_is(pages)
    
    def test_page_and_chapter_added(self):
        update_page_metadata(self.content)
        page_metadata = PageMetadata.objects.filter(content=self.content)
        the(page_metadata).length_is(2)
        
        self.content.file.contents = build_content_with_chapter(pages=2)
        update_page_metadata(self.content)
        page_metadata = PageMetadata.objects.filter(content=self.content)
        the(page_metadata).length_is(3)
        
    def test_change_page_title(self):
        pass 
    
    def test_page_metadata_disabled(self):
        self.content.enable_page_metadata = False
        self.content.save()
        update_page_metadata(self.content)
        page_metadata = PageMetadata.objects.filter(content=self.content)
        the(page_metadata).length_is(0)
    
def build_content(pages=1, _from=0):
    ic = XMLBuilder('interactiveContent', name='Animals and plant cells')
    ic.metadata
    ic.addons
    ic.assets
    with ic.pages:
        for x in range(_from, pages):
            ic.page(id='YNfds%s' % x, name='Animals', href='79743892754%s' % x, preview='', reportable='true')
    return str(ic)

def build_content_with_chapter(pages=1, _from=0):
    ic = XMLBuilder('interactiveContent', name='Animals and plant cells')
    ic.metadata
    ic.addons
    ic.assets
    with ic.pages:
        for x in range(_from, pages):
            ic.page(id='YNfds%s' % x, name='Animals', href='79743892754%s' % x, preview='', reportable='true')
        with ic.chapter:
            ic.page(id='YNfdsC', name='Animals', href='797438927540', preview='', reportable='true')
    return str(ic)