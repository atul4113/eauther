from src.libraries.utility.trackers import FunctionCallsTracker
from src.libraries.utility.noseplugins import FormattedOutputTestCase
from nose.plugins.attrib import attr

class TrackersTests(FormattedOutputTestCase):
    def setUp(self):
        self.fct = FunctionCallsTracker()

    def tearDown(self):
        pass

    @attr('unit')
    def test_function_called_3_times(self):
        self.fct.call("open()")
        self.fct.call("open()")
        self.fct.call("open()")
        self.assertEqual(self.fct.called("open()"), 3)

    @attr('unit')
    def test_function_not_called(self):
        self.fct.call("close()")
        self.fct.call("size()")
        self.fct.call("width()")
        self.assertEqual(self.fct.called("open()"), 0)

    @attr('unit')
    def test_any_function_called(self):
        self.fct.call("close()")
        self.fct.call("size()")
        self.fct.call("width()")
        self.assertEqual(self.fct.called(), 3)