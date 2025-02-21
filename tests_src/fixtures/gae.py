import pytest
from djangae.test_runner import init_testbed
from google.appengine.api import apiproxy_stub_map
from google.appengine.api import memcache
from djangae.db.backends.appengine import caching
from pytest_django.fixtures import db

@pytest.fixture
def init_stubs():
    """
        Init stubs without database configuration
    """
    init_testbed()


@pytest.fixture
def database_cleaner():
    yield
    datastore = apiproxy_stub_map.apiproxy.GetStub("datastore_v3")
    if datastore is not None:
        datastore.Clear()
        memcache.flush_all()
        caching.get_context().reset()

