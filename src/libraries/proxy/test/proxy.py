from django.test.client import Client
import google.appengine.api.urlfetch
from minimock import mock, restore
from src.libraries.utility.noseplugins import FormattedOutputTestCase
from src.libraries.utility.test_assertions import status_code_for, the
from src.libraries.utility.trackers import FunctionCallsTracker, verify

class StubbedResponse(object):
    status_code = 200
    content = "OK"

class ProxyTests(FormattedOutputTestCase):
    def setUp(self):
        self.client = Client()

    def tearDown(self):
        restore()

    def test_get_local_url(self):
        mock("google.appengine.api.urlfetch.fetch", returns=StubbedResponse())
        response = self.client.get("/proxy/get?url=http://testserver/public/video/getaddon")
        status_code_for(response).should_be(302)

    def test_get_remote_url(self):
        mock("google.appengine.api.urlfetch.fetch", returns=StubbedResponse())
        response = self.client.get("/proxy/get?url=http://wp.pl")
        status_code_for(response).should_be(200)
        the(response.content).is_not_none()
        the(response.content).equals('OK')

    def test_cached_calls(self):
        tracker = FunctionCallsTracker()
        mock("google.appengine.api.urlfetch.fetch", returns=StubbedResponse(), tracker=tracker)
        self.client.get("/proxy/get?url=http://wp.pl")
        self.client.get("/proxy/get?url=http://wp.pl")
        verify(tracker).recorded('google.appengine.api.urlfetch.fetch').once()

    def test_uncached_calls(self):
        tracker = FunctionCallsTracker()
        mock("google.appengine.api.urlfetch.fetch", returns=StubbedResponse(), tracker=tracker)
        self.client.get("/proxy/get?url=http://wp.pl")
        self.client.get("/proxy/get?url=http://onet.pl")
        verify(tracker).recorded('google.appengine.api.urlfetch.fetch').times(2)