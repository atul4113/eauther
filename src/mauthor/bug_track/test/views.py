from django.test.client import Client
from src.libraries.utility.noseplugins import FormattedOutputTestCase
from src.libraries.utility.test_assertions import status_code_for
from src.mauthor.bug_track.models import Bug

class ViewsTests(FormattedOutputTestCase):
    fixtures = ['bug.json']

    def setUp(self):
        self.client = Client()
        self.client.login(username='owner1', password='owner1')

    def tearDown(self):
        self.client.logout()
        
    def test_add_bug_positive(self):
        bugs_count_before = len(Bug.objects.filter(content__id=1226))
        response = self.client.post('/corporate/view/1226', {'title' : 'bug', 'description' : 'big bug', 'next' : '/corporate/list/22'}, follow=True)
        status_code_for(response).should_be(200)
        bugs_count_after = len(Bug.objects.filter(content__id=1226))
        self.assertNotEqual(bugs_count_after, bugs_count_before)
        
    def test_add_bug_negative(self):
        bugs_count_before = len(Bug.objects.filter(content__id=1226))
        response = self.client.post('/corporate/view/1226', {'title' : '', 'description' : 'big bug', 'next' : '/corporate/list/22'}, follow=True)
        status_code_for(response).should_be(200)
        bugs_count_after = len(Bug.objects.filter(content__id=1226))
        self.assertEqual(bugs_count_after, bugs_count_before)
        
    def test_delete_bug_positive(self):
        response = self.client.post('/corporate/view/1226', {'title' : 'bug', 'description' : 'big bug', 'next' : '/corporate/list/22'}, follow=True)
        status_code_for(response).should_be(200)
        bug = Bug.objects.latest('created_date')
        bugs_count_before = len(Bug.objects.filter(content__id=1226))
        response = self.client.get('/bug_track/%(id)s/delete?next=/corporate/list/22' % {'id' : bug.id})
        status_code_for(response).should_be(302)
        self.assertRedirects(response, '/corporate/view/1226?next=/corporate/list/22')
        bugs_count_after = len(Bug.objects.filter(content__id=1226))
        self.assertNotEqual(bugs_count_after, bugs_count_before)
        
    def test_delete_bug_negative(self):
        response = self.client.post('/corporate/view/1226', {'title' : 'bug', 'description' : 'big bug', 'next' : '/corporate/list/22'}, follow=True)
        status_code_for(response).should_be(200)
        self.client.logout()
        self.client.login(username='kgebert', password='kgebert1')
        bug = Bug.objects.latest('created_date')
        response = self.client.get('/bug_track/%(id)s/delete?next=/corporate/list/22' % {'id' : bug.id})
        status_code_for(response).should_be(404)