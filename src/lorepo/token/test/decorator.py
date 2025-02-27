import django.shortcuts
from src.minimock import mock, restore
from src.lorepo.token.decorators import token
from src.libraries.utility.trackers import FunctionCallsTracker
from src.libraries.utility.noseplugins import FormattedOutputTestCase
from src.nose.plugins.attrib import attr

class StubbedRequest(object):
    def __init__(self):
        self.META = {}
        self.session = {}
        self.POST = {}
        self.GET = {}
        self.path = ''

def method_to_call(request):
    pass

class DecoratorTests(FormattedOutputTestCase):
    def setUp(self):
        self.fct = FunctionCallsTracker()
        mock("method_to_call", tracker=self.fct)
        mock("django.shortcuts.render")

    def tearDown(self):
        restore()

    @attr('unit')
    def test_session_and_request_not_the_same(self):
        request = StubbedRequest()
        request.META["HTTP_REFERER"] = "/mycontent"
        request.session["token_a"] = "k4r0l"
        request.GET["_TOKEN"] = "m4te0"
        token('a', method_to_call)(request)
        self.assertEqual(self.fct.called(), 0)

    @attr('unit')
    def test_session_and_request_the_same(self):
        request = StubbedRequest()
        request.META["HTTP_REFERER"] = "/mycontent"
        request.session["token_a"] = "k4r0l"
        request.GET["_TOKEN"] = "k4r0l"
        token('a', method_to_call)(request)
        self.assertEqual(self.fct.called(), 1)

    @attr('unit')
    def test_session_missing(self):
        request = StubbedRequest()
        request.META["HTTP_REFERER"] = "/mycontent"
        request.GET["_TOKEN"] = "k4r0l"
        token('a', method_to_call)(request)
        self.assertEqual(self.fct.called(), 1)

    @attr('unit')
    def test_request_missing(self):
        request = StubbedRequest()
        request.META["HTTP_REFERER"] = "/mycontent"
        request.session["token_a"] = "k4r0l"
        token('a', method_to_call)(request)
        self.assertEqual(self.fct.called(), 1)
