from src.libraries.utility.noseplugins import FormattedOutputTestCase
from minimock import restore, mock
from src.libraries.utility.urlfetch import fetch
from google.appengine.api import urlfetch
from src.libraries.utility.test_assertions import the
from src.libraries.utility.trackers import FunctionCallsTracker, verify
from nose.plugins.attrib import attr

class StubbedResponse():
    def __init__(self, status_code, content):
        self.status_code = status_code
        self.content = content

class TrackersTests(FormattedOutputTestCase):
    def tearDown(self):
        restore()

    @attr('unit')
    def test_positive_fetch(self):
        mock('urlfetch.fetch', returns=StubbedResponse(200, 'OK'))
        content = fetch('http://www.mauthor.com')
        the(content).is_not_none()
        the(content).equals('OK')

    @attr('unit')
    def test_negative_fetch(self):
        mock('urlfetch.fetch', returns=StubbedResponse(404, 'OK'))
        content = fetch('http://www.mauthor.com')
        the(content).is_none()

    @attr('unit')
    def test_uncached_fetch(self):
        tracker = FunctionCallsTracker()
        mock('urlfetch.fetch', returns=StubbedResponse(200, 'OK'), tracker=tracker)
        content = fetch('http://www.mauthor.com')
        the(content).is_not_none()
        content = fetch('http://www.mauthor.com')
        the(content).is_not_none()
        verify(tracker).recorded('urlfetch.fetch').times(2)

    @attr('unit')
    def test_cached_fetch(self):
        tracker = FunctionCallsTracker()
        cache_time = 60 * 60 * 2
        mock('urlfetch.fetch', returns=StubbedResponse(200, 'OK'), tracker=tracker)
        content = fetch('http://www.mauthor.com', cache_time=cache_time)
        the(content).is_not_none()
        content = fetch('http://www.mauthor.com', cache_time=cache_time)
        the(content).is_not_none()
        verify(tracker).recorded('urlfetch.fetch').once()

    @attr('unit')
    def test_empty_response(self):
        mock('urlfetch.fetch', returns=StubbedResponse(200, ''))
        content = fetch('http://www.mauthor.com')
        the(content).is_none()