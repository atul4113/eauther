from lorepo.mycontent.forms import AddAddonForm
from libraries.utility.noseplugins import FormattedOutputTestCase
from nose.plugins.attrib import attr

class FormsTests(FormattedOutputTestCase):
    @attr('unit')
    def test_validate_name_positive(self):
        '''Name easily convertable to valid JS variable identifier should be allowed.
        '''
        form = AddAddonForm({'title' : 'Presentation title', 'name' : 'presentation_title', 'score_type' : 'last'})
        self.assertTrue(form.is_valid())

        form = AddAddonForm({'title' : 'Presentation title', 'name' : 'presentation title', 'score_type' : 'last'})
        self.assertTrue(form.is_valid())

        form = AddAddonForm({'title' : 'Presentation title', 'name' : 'presentation title 123', 'score_type' : 'last'})
        self.assertTrue(form.is_valid())

        form = AddAddonForm({'title' : 'Presentation title', 'name' : '1presentation_title', 'score_type' : 'last'})
        self.assertTrue(form.is_valid())

        form = AddAddonForm({'title' : 'Presentation title', 'name' : 'test!@#$%^&*()-+=;:"\'.,/\?><|[]{}', 'score_type' : 'last'})
        self.assertTrue(form.is_valid())

        form = AddAddonForm({'title' : 'Presentation title', 'name' : 'test!@#$%^&*()-+=;:"\'.,/\?><|[]{}test', 'score_type' : 'last'})
        self.assertTrue(form.is_valid())

        form = AddAddonForm({'title' : 'Presentation title', 'name' : 'test!@#$%^&*()-+=;test;"\'.,/\?><|[]{}', 'score_type' : 'last'})
        self.assertTrue(form.is_valid())

    @attr('unit')
    def test_validate_name_negative(self):
        '''Names not convertable to valid JS variable identifier should not be allowed.
        '''
        form = AddAddonForm({'title' : 'Presentation title', 'name' : '!@#$%^&*()-+=;:"\'.,/\?><|[]{}'})
        result = form.is_valid()
        self.assertFalse(result)

        form = AddAddonForm({'title' : 'Presentation title', 'name' : '123'})
        self.assertFalse(form.is_valid())

        form = AddAddonForm({'title' : 'Presentation title', 'name' : '     '})
        self.assertFalse(form.is_valid())

        form = AddAddonForm({'title' : 'Presentation title'})
        self.assertFalse(form.is_valid())