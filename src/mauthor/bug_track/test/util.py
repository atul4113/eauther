from django.test.client import Client
from src.libraries.utility.noseplugins import FormattedOutputTestCase
from src.lorepo.spaces.models import Space
from django.contrib.auth.models import User

class UtilTests(FormattedOutputTestCase):
    fixtures = ['bug.json']

    def setUp(self):
        pass

    def tearDown(self):
        pass