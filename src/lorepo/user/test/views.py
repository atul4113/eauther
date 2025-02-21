from django.test.client import Client
from django.contrib.auth.models import User
from libraries.utility.noseplugins import FormattedOutputTestCase

class ViewsTest(FormattedOutputTestCase):
    fixtures = ['user.json']

    def setUp(self):
        self.client = Client()
        self.client.login(username='kgebert', password='kgebert1')
        
    def test_url_profile(self):
        response = self.client.get('/user/profile')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['request'].user.username, 'kgebert')
        self.assertEqual(response.context['request'].user.email, 'karol.gebert@solwit.pl')
    
    def test_change_password(self):
        password_before = User.objects.get(username='kgebert').password
        response = self.client.post('/user/profile', { "old_password" : "kgebert1", "new_password1" : "karol", "new_password2" : "karol" })
        password_after = User.objects.get(username='kgebert').password
        self.assertEqual(response.context['password_form'].data["old_password"], "kgebert1")
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(password_before, password_after)
        
    def test_change_email(self):
        email_before = User.objects.get(username='kgebert').email
        response = self.client.post('/user/profile', { "email" : "karol@karol.pl" })
        email_after = User.objects.get(username='kgebert').email
        self.assertEqual(email_after, "karol@karol.pl")
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(email_before, email_after)