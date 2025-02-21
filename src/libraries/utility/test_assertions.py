def status_code_for(response):
    '''Allows fluent response status code assertion.

    Eg. to check if response code is 200 use:
    status_code_for(response).should_be(200)
    '''
    class StatusCodeAssertion():
        def __init__(self, response):
            self.response = response

        def should_be(self, code):
            if self.response.status_code != int(code):
                raise AssertionError("Response status code is %s and it should be %s" % (self.response.status_code, code))

    return StatusCodeAssertion(response)

def the(object_under_test):
    '''Allows fluent object assertions.
    '''

    class ObjectAssertion():
        def __init__(self, object_under_test):
            self.object_under_test = object_under_test

        def is_none(self):
            if self.object_under_test is not None:
                raise AssertionError("This object should be None while it is <%s>" % (self.object_under_test))

        def is_not_none(self):
            if self.object_under_test is None:
                raise AssertionError("This object is not None.  It is <%s>" % (self.object_under_test))

        def equals(self, value):
            if self.object_under_test != value:
                raise AssertionError("<%s> does not equal <%s> and it should" % (self.object_under_test, value))

        def does_not_equal(self, value):
            if self.object_under_test == value:
                raise AssertionError("<%s> equals <%s> and it shouldn't" % (self.object_under_test, value))

        def length_is(self, value):
            if len(self.object_under_test) != value:
                raise AssertionError("Length is <%s> and it should be <%s>" % (len(self.object_under_test), value))

        def contains_key(self, key, value):
            if key not in self.object_under_test or self.object_under_test[key] != value:
                raise AssertionError("<%s> does not contain key <%s> with value <%s>" % (self.object_under_test, key, value))

    return ObjectAssertion(object_under_test)


def context_of(response):
    class ContextAssertion():
        def __init__(self, response):
            self.response = response

        def shoud_contains(self, value):
            if not value in self.response.context:
                raise AssertionError("Context <%s> does not contains <%s>" % (self.response.context, value))

            return self.response.context[value]

    return ContextAssertion(response)