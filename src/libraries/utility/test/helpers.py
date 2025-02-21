from libraries.utility.noseplugins import FormattedOutputTestCase
from django.http import QueryDict
from libraries.utility.helpers import parse_query_dict
from libraries.utility.test_assertions import the
from nose.plugins.attrib import attr

class HelpersTests(FormattedOutputTestCase):
    
    @attr('unit')
    def test_parse_query_dict(self):
        query_dict = QueryDict('tags[1]=ABC&tags[2]=DEF&tags[xyz]=GHI')
        parameters = parse_query_dict(query_dict)
        the(parameters.tags).is_not_none()
        the(parameters.tags['1']).equals(['ABC'])
        the(parameters.tags['2']).equals(['DEF'])
        the(parameters.tags['xyz']).equals(['GHI'])