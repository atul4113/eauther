from minimock import AbstractTracker

class FunctionCallsTracker(AbstractTracker):

    def __init__(self):
        self.calls = []

    def called(self, func_name=None):
        if func_name is not None:
            calls = [call for call in self.calls if {'func_name' : func_name } == call]
            return len(calls)
        return len(self.calls)

    def call(self, func_name, *args, **kw):
        self.calls.append({'func_name' : func_name })

def verify(tracker):
    class TrackerAssertion():
        def __init__(self, tracker):
            self.tracker = tracker

        def recorded(self, func_name):
            class CallsAssertion():
                def __init__(self, tracker, func_name):
                    self.tracker = tracker
                    self.__name__ = func_name

                def once(self):
                    called = self.tracker.called(self.__name__)
                    if called > 1:
                        raise AssertionError("Function <%s> has been called %s times" % (self.__name__, called))
                    if called == 0:
                        raise AssertionError("Function <%s> has not been called" % (self.__name__))

                def times(self, count):
                    called = self.tracker.called(self.__name__)
                    if called != count:
                        raise AssertionError("Function <%s> has been called %s times and is should be called %s times" % (self.__name__, called, count))

            return CallsAssertion(self.tracker, func_name)

    return TrackerAssertion(tracker)