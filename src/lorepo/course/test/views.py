from libraries.utility.noseplugins import FormattedOutputTestCase
from django.test.client import Client

class UserWithoutPermissionCourseTests(FormattedOutputTestCase):
    fixtures = ['course_views.json']

    def setUp(self):
        self.client = Client()
        self.client.login(username='test', password='test')

    def tearDown(self):
        self.client.logout()

    def test_should_not_see_manage_courses_in_menu(self):
        response = self.client.get('/corporate/list/5699868278390784')
        submenu_titles = [sub[0] for sub in response.context['sub_menus']]

        self.assertFalse('Manage Courses' in submenu_titles)

    def test_can_not_list_courses(self):
        response = self.client.get('/course/list/5699868278390784')

        self.assertEqual(403, response.status_code)

    def test_can_not_rename_course(self):
        response = self.client.get('/course/rename/6227633859723264')

        self.assertEqual(403, response.status_code)

    def test_can_not_remove_course(self):
        response = self.client.get('/course/remove/6227633859723264')

        self.assertEqual(403, response.status_code)

    def test_can_not_edit_table_of_contents(self):
        response = self.client.get('/course/edit_table_of_contents/6227633859723264/5699868278390784')

        self.assertEqual(403, response.status_code)

    def test_can_not_remove_chapter(self):
        response = self.client.get('/course/remove_chapter/2/6227633859723264')

        self.assertEqual(403, response.status_code)

    def test_can_not_export_course(self):
        response = self.client.get('/course/export/6227633859723264')

        self.assertEqual(403, response.status_code)

class UserWithPermissionCourseTests(FormattedOutputTestCase):
    fixtures = ['course_views.json']

    def setUp(self):
        self.client = Client()
        self.client.login(username='kgebert', password='kgebert1')

    def tearDown(self):
        self.client.logout()

    def test_should_see_manage_courses_in_menu(self):
        response = self.client.get('/corporate/list/5699868278390784')
        submenu_titles = [sub[0] for sub in response.context['sub_menus']]

        self.assertTrue('Manage Courses' in submenu_titles)

    def test_can_list_courses(self):
        response = self.client.get('/course/list/5699868278390784')

        self.assertEqual(200, response.status_code)

    def test_can_rename_course(self):
        response = self.client.get('/course/rename/6227633859723264')

        self.assertEqual(200, response.status_code)

    def test_can_remove_course(self):
        response = self.client.get('/course/remove/6227633859723264')

        self.assertEqual(302, response.status_code)

    def test_can_edit_table_of_contents(self):
        response = self.client.get('/course/edit_table_of_contents/6227633859723264/5699868278390784')

        self.assertEqual(200, response.status_code)

    def test_can_remove_chapter(self):
        response = self.client.get('/course/remove_chapter/2/6227633859723264')

        self.assertEqual(302, response.status_code)