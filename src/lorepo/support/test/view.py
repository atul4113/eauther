from src.libraries.utility.noseplugins import FormattedOutputTestCase
from django.test.client import Client
from src.libraries.utility.test_assertions import status_code_for, the

class AdminViewsTests(FormattedOutputTestCase):
    fixtures = ['support.json']

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        self.client.logout()

    def test_admin_index(self):
        self.client.login(username='kgebert', password='kgebert1')
        response = self.client.get('/support/admin')
        status_code_for(response).should_be(200)

    def test_admin_index_no_privileges(self):
        self.client.login(username='test', password='test')
        response = self.client.get('/support/admin')
        status_code_for(response).should_be(200)
        for ticket in response.context['tickets']:
            the(ticket.assigned_to.username).equals('test')

    def test_admin_ticket(self):
        self.client.login(username='kgebert', password='kgebert1')
        response = self.client.get('/support/admin/ticket/22')
        status_code_for(response).should_be(200)

    def test_admin_ticket_no_privileges(self):
        self.client.login(username='test', password='test')
        response = self.client.get('/support/admin/ticket/22')
        status_code_for(response).should_be(302)

    def test_user_without_company_index(self):
        self.client.login(username='test2', password='test')
        response = self.client.get('/support')
        status_code_for(response).should_be(302)

    def test_user_without_company_ticket(self):
        self.client.login(username='test2', password='test')
        response = self.client.get('/support/ticket/22')
        status_code_for(response).should_be(302)