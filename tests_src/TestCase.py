import pytest
from djangae.test import HandlerAssertionsMixin, TestCaseMixin

from tests_src.mixins.cache import CacheCleanerMixin


class BaseTestMixin(object):
    def setUp(self):
        """
            Last call of this method in chain
        """
        pass

    def assertEqual(self, a, b):
        assert a == b


class _TestCase(CacheCleanerMixin, HandlerAssertionsMixin, TestCaseMixin, BaseTestMixin):
    pass


class TestCase(_TestCase):
    """
        Test case which contains basic features like cleaning cache or possibility to queue testing.
    """
    @pytest.fixture(autouse=True)
    def __setUp(self, init_stubs):
        """
            Call setup for rest of classes for each test.
        """
        self.setUp()


@pytest.mark.django_db
class DBTestCase(_TestCase):
    """
        If tests needs connection to database then should inherit from this test case. For each test case database
        will be cleared.
    """

    @pytest.fixture(autouse=True)
    def __setUp(self, init_stubs, db, request, database_cleaner):
        """
            Call setup for rest of classes for each test.
        """
        self.setUp()