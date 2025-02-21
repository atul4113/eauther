from libraries.utility.noseplugins import FormattedOutputTestCase
from mauthor.backup.utils import make_path, get_path
from nose.plugins.attrib import attr


class ZipMockup:
    def __init__(self, content_id, content_title, version):
        if version == 0 :
            self.path = "%s - %s/" % (content_id, content_title)
        elif version == 1 :
            self.path = make_path(content_id, content_title)

    def read(self, path):
        if (path != self.path + 'metadata.xml'):
            raise KeyError


class BackupUtilsTest(FormattedOutputTestCase):
    content_id = 123456789
    default_title = 'Simple: lesson???'

    @attr('unit')
    def test_make_simple_path(self):
        title = 'Simple lesson'
        path = make_path(self.content_id, title)
        expected_path = '123456789 - Simple lesson/'
        self.assertEqual(path, expected_path)

    @attr('unit')
    def test_make_path_from_lesson_with_special_characters(self):
        title = 'Simple /\?<>:\*\|"\^\\\ lesson'
        path = make_path(self.content_id, title)
        expected_path = '123456789 - Simple _ lesson/'
        self.assertEqual(path, expected_path)

    @attr('unit')
    def test_make_path_from_lesson_with_special_chars_in_few_places(self):
        title = 'Simple: lesson???'
        path = make_path(self.content_id, title)
        expected_path = '123456789 - Simple_ lesson_/'
        self.assertEqual(path, expected_path)

    @attr('unit')
    def test_make_path_from_lesson_with_long_title(self):
        title = 'Title ' * 50  # title with 300 chars
        path = make_path(self.content_id, title)
        self.assertEqual(len(path), 256)

    @attr('unit')
    def test_make_path_from_lesson_with_title_less_than_255_chars(self):
        title = 'A' * 250  # title with 300 chars
        path = make_path(self.content_id, title)
        self.assertEqual(len(path), 256)

    @attr('unit')
    def test_get_old_path(self):
        zip = ZipMockup(self.content_id, self.default_title, 0)
        path = get_path(zip, self.content_id, self.default_title)
        self.assertEqual(path, "%s - %s/" % (self.content_id, self.default_title))

    @attr('unit')
    def test_get_new_path(self):
        zip = ZipMockup(self.content_id, self.default_title, 1)
        path = get_path(zip, self.content_id, self.default_title)
        self.assertEqual(path, make_path(self.content_id, self.default_title))

    @attr('unit')
    def test_really_broken_path(self):
        zip = ZipMockup(self.content_id, self.default_title, 1)
        zip.path = 'Broken ' + zip.path
        error = False
        try:
            path = get_path(zip, self.content_id, self.default_title)
        except KeyError:
            error = True
        self.assertTrue(error)