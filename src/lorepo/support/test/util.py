from src.libraries.utility.noseplugins import FormattedOutputTestCase
from src.nose.plugins.attrib import attr
from src.lorepo.support.util import parse_lesson_id
from src.libraries.utility.test_assertions import the

class SupportUtilTests(FormattedOutputTestCase):
    @attr('unit')
    def test_match_embed_url(self):
        url = 'http://www.mauthor.com/embed/12345678'
        lesson_id = parse_lesson_id(url)
        the(lesson_id).equals('12345678')

    @attr('unit')
    def test_match_mycontent_url(self):
        url = 'http://www.mauthor.com/mycontent/view/12345678?next=a'
        lesson_id = parse_lesson_id(url)
        the(lesson_id).equals('12345678')

    @attr('unit')
    def test_match_corporate_url(self):
        url = 'http://www.mauthor.com/corporate/view/12345678'
        lesson_id = parse_lesson_id(url)
        the(lesson_id).equals('12345678')

    @attr('unit')
    def test_match_localhost_url(self):
        url = 'http://localhost:8080/mycontent/view/6315045034131456?next=/mycontent/6244676289953792'
        lesson_id = parse_lesson_id(url)
        the(lesson_id).equals('6315045034131456')
