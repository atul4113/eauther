from src.libraries.utility.noseplugins import FormattedOutputTestCase
from django.contrib.auth.models import User
from src.libraries.utility.test_assertions import status_code_for

class ReadAccessUserTests(FormattedOutputTestCase):
    fixtures = ['permission_views.json']

    def setUp(self):
        self.test_user = User.objects.get(username = 'test')
        self.client.login(username = 'test', password = 'test')

    def tearDown(self):
        self.client.logout()

    def test_can_see_list_of_lessons(self):
        response = self.client.get('/corporate/list/58')

        status_code_for(response).should_be(200)

    def test_can_preview_lesson(self):
        response = self.client.get('/corporate/view/68?next=/corporate/list/58')

        status_code_for(response).should_be(200)

    def test_can_report_new_bug_in_bugtrack(self):
        response = self.client.post('/corporate/view/68', { 'next' : '/corporate/list/58', 'title' : 'test', 'description' : 'test' })

        status_code_for(response).should_be(302)

    def test_can_NOT_add_new_lesson(self):
        response = self.client.post('/mycontent/addcontent/59?next=/corporate/list/59', { 'title' : 'test' })

        status_code_for(response).should_be(403)

    def test_can_NOT_make_lesson_public(self):
        response = self.client.get('/corporate/68/makepublic?next=/corporate/list/58#68')

        status_code_for(response).should_be(403)

    def test_can_NOT_edit_space(self):
        response = self.client.get('/corporate/projects/58')

        status_code_for(response).should_be(403)

    def test_can_NOT_manage_access(self):
        response = self.client.get('/permission')

        status_code_for(response).should_be(403)

class WriteAccessUserTests(FormattedOutputTestCase):
    fixtures = ['permission_views.json']

    def setUp(self):
        super(WriteAccessUserTests, self).setUp()
        self.test_user = User.objects.get(username = 'test2')
        self.client.login(username = 'test2', password = 'test')

    def tearDown(self):
        super(WriteAccessUserTests, self).tearDown()
        self.client.logout()

    def test_can_add_lesson(self):
        response = self.client.post('/mycontent/addcontent/59?next=/corporate/list/59', { 'title' : 'test' })

        status_code_for(response).should_be(302)

    def test_can_make_lesson_public(self):
        response = self.client.get('/corporate/68/makepublic?next=/corporate/list/58#68')

        status_code_for(response).should_be(302)

    def test_can_edit_space(self):
        response = self.client.get('/corporate/projects/58')

        status_code_for(response).should_be(200)

    def test_can_start_localization(self):
        response = self.client.get('/localization/start_localization/68/58?next=/corporate/list/58')

        status_code_for(response).should_be(200)

    def test_can_NOT_upload_corporate_logo(self):
        response = self.client.get('/corporate/upload')

        status_code_for(response).should_be(403)

    def test_can_NOT_view_corporate_details(self):
        response = self.client.get('/company/details/12')

        status_code_for(response).should_be(403)

    def test_can_NOT_view_corporate_panel(self):
        response = self.client.get('/corporate/admin')

        status_code_for(response).should_be(403)

    def test_can_NOT_edit_corproate_details(self):
        response = self.client.get('/company/edit/12')

        status_code_for(response).should_be(403)

    def test_can_NOT_manage_access(self):
        response = self.client.get('/permission')

        status_code_for(response).should_be(403)

class OwnerAccessUserTests(FormattedOutputTestCase):
    fixtures = ['permission_views.json']

    def setUp(self):
        self.test_user = User.objects.get(username = 'kgebert')
        self.client.login(username = 'kgebert', password = 'kgebert1')

    def tearDown(self):
        self.client.logout()

    def test_can_upload_corporate_logo(self):
        response = self.client.get('/corporate/upload')

        status_code_for(response).should_be(200)

    def test_can_view_corporate_details(self):
        response = self.client.get('/company/details/12')

        status_code_for(response).should_be(200)

    def test_can_view_corporate_panel(self):
        response = self.client.get('/corporate/admin')

        status_code_for(response).should_be(200)

    def test_can_edit_details(self):
        response = self.client.get('/company/edit/12')

        status_code_for(response).should_be(200)

    def test_can_manage_access(self):
        response = self.client.get('/permission')

        status_code_for(response).should_be(200)