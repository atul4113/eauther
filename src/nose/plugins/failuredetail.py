"""
This plugin provides assert introspection. When the plugin is enabled
and a test failure occurs, the traceback is displayed with extra context
around the line in which the exception was raised. Simple variable 
substitution is also performed in the context output to provide more
debugging information.
"""
    
from nose.plugins import Plugin
from nose.inspector import inspect_traceback

class FailureDetail(Plugin):
    """
    Plugin that provides extra information in tracebacks of test failures.
    """
    score = 600 # before capture
    
    def options(self, parser, env):
        """Register commmandline options.
        """
        parser.add_option(
            "-d", "--detailed-errors", "--failure-detail",
            action="store_true",
            default=env.get('NOSE_DETAILED_ERRORS'),
            dest="detailedErrors", help="Add detail to error"
            " output by attempting to evaluate failed"
            " asserts [NOSE_DETAILED_ERRORS]")

    def configure(self, options, conf):
        """Configure plugin.
        """
        if not self.can_configure:
            return
        self.enabled = options.detailedErrors
        self.conf = conf

    def formatFailure(self, test, err):
        """Add detail from traceback inspection to error message of a failure.
        """
        ec, ev, tb = err
        tbinfo = inspect_traceback(tb)
        test.tbinfo = tbinfo
        return (ec, '\n'.join([str(ev), tbinfo]), tb)
