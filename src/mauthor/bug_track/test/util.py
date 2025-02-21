from django.test.client import Client
from libraries.utility.noseplugins import FormattedOutputTestCase
from lorepo.spaces.models import Space
from django.contrib.auth.models import User

class UtilTests(FormattedOutputTestCase):
    fixtures = ['bug.json']

    def setUp(self):
        pass

    def tearDown(self):
        pass