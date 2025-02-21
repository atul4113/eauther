from lorepo.mycontent.models import Content
from lorepo.filestorage.models import UploadedFile
from lorepo.assets.util import update_content_assets, update_asset_title,\
    delete_asset
import xml.dom.minidom
from lorepo.assets.templatetags.assets import thumbnail_url
from libraries.utility.noseplugins import FormattedOutputTestCase

class AssetsTests(FormattedOutputTestCase):
    fixtures = ['assets.json']

    def test_update_content(self):
        uploaded_file = UploadedFile.objects.get(pk=28)
        uploaded_file.title = 'Some title'
        content = Content.objects.get(pk=107)

        doc = xml.dom.minidom.parseString(content.file.contents)
        assets = doc.getElementsByTagName('asset')
        self.assertEqual(2, len(assets))

        update_content_assets(content, uploaded_file)
        content = Content.objects.get(pk=107)
        doc = xml.dom.minidom.parseString(content.file.contents)
        assets = doc.getElementsByTagName('asset')
        self.assertEqual(3, len(assets))
        asset = assets[2]
        self.assertEqual(asset.getAttribute('href'), '/file/serve/%(id)s' % {'id' : uploaded_file.id})
        self.assertEqual(asset.getAttribute('type'), 'image')
        self.assertEqual(asset.getAttribute('title'), 'Some title')

        uploaded_file.content_type = 'audio/mp3'
        uploaded_file.title = 'Another title'
        update_content_assets(content, uploaded_file)
        content = Content.objects.get(pk=107)
        doc = xml.dom.minidom.parseString(content.file.contents)
        assets = doc.getElementsByTagName('asset')
        self.assertEqual(4, len(assets))
        asset = assets[3]
        self.assertEqual(asset.getAttribute('type'), 'audio')
        self.assertEqual(asset.getAttribute('title'), 'Another title')

    def test_update_asset_title(self):
        '''Asset title should be updateable
        '''
        content = Content.objects.get(pk=107)
        doc = xml.dom.minidom.parseString(content.file.contents)
        assets = doc.getElementsByTagName('asset')
        href = assets[0].getAttribute('href')
        update_asset_title(content, href, 'Brand new title')

        content = Content.objects.get(pk=107)
        doc = xml.dom.minidom.parseString(content.file.contents)
        assets = doc.getElementsByTagName('asset')
        asset = assets[0]
        self.assertEqual(asset.getAttribute('title'), 'Brand new title')

    def test_thumbnail_url_filter(self):
        url = thumbnail_url('/file/serve/123')
        self.assertEqual(url, '/file/thumbnail/123/150/150')
        url = thumbnail_url('/file/serve/123', '180,210')
        self.assertEqual(url, '/file/thumbnail/123/180/210')
        url = thumbnail_url('123', '180,210')
        self.assertEqual(url, '')

    def test_delete_asset(self):
        content = Content.objects.get(pk=107)
        doc = xml.dom.minidom.parseString(content.file.contents)
        assets = doc.getElementsByTagName('asset')
        self.assertEqual(2, len(assets))
        href = assets[0].getAttribute('href')
        delete_asset(content, href)

        content = Content.objects.get(pk=107)
        doc = xml.dom.minidom.parseString(content.file.contents)
        assets = doc.getElementsByTagName('asset')
        self.assertEqual(1, len(assets))