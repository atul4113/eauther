import libraries.utility.timing as Timing
import logging
from libraries.utility.noseplugins import FormattedOutputTestCase
from nose.plugins.attrib import attr

class TimingTests(FormattedOutputTestCase):
    def setUp(self):
        Timing.clear()

    @attr('unit')
    def test_start(self):
        self.assertIsNone(Timing.get_current())

        Timing.start('START')
        self.assertIsNotNone(Timing.get_current())
        self.assertEqual(Timing.get_current(), 'START')

        Timing.start('INNER_START')
        self.assertIsNotNone(Timing.get_current())
        self.assertEqual(Timing.get_current(), 'INNER_START')

    @attr('unit')
    def test_end(self):
        self.assertIsNone(Timing.get_current())
        Timing.start('START 1')
        Timing.end('START 1')
        self.assertIsNone(Timing.get_current())

        self.assertIsNone(Timing.get_current())
        Timing.start('START 2')
        self.assertEqual(Timing.get_current(), 'START 2')
        Timing.start('INNER_START')
        self.assertEqual(Timing.get_current(), 'INNER_START')
        Timing.end('INNER_START')
        self.assertIsNotNone(Timing.get_current())
        self.assertEqual(Timing.get_current(), 'START 2')
        Timing.end('START 2')
        logging.error(Timing.get_times())

    @attr('unit')
    def test_incorrect_end(self):
        Timing.start('START')
        self.assertRaises(Exception, Timing.end, 'INNER_START')