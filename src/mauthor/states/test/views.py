from django.test.client import Client
from src.mauthor.states.models import State, StatesSet, ContentState
from src.lorepo.mycontent.models import Content
from src.libraries.utility.noseplugins import FormattedOutputTestCase

class ViewsTests(FormattedOutputTestCase):
    fixtures = ['states.json']

    def setUp(self):
        self.client = Client()
        self.client.login(username='test', password='test')

    def tearDown(self):
        self.client.logout()

    def test_percentage_change(self):
        response = self.client.get('/states/update_percentage/318/27')
        self.assertEqual(response.status_code, 200)
        state = State.objects.get(pk=318)
        self.assertEqual(state.percentage, 27)

    def test_update_rank_higher(self):
        response = self.client.get('/states/update_rank/318/2')
        self.assertEqual(response.status_code, 200)
        state = State.objects.get(pk=318)
        self.assertEqual(state.rank, 2)
        state = State.objects.get(pk=320)
        self.assertEqual(state.rank, 0)
        state = State.objects.get(pk=322)
        self.assertEqual(state.rank, 1)
        state = State.objects.get(pk=324)
        self.assertEqual(state.rank, 3)

    def test_update_rank_lower(self):
        response = self.client.get('/states/update_rank/322/0')
        self.assertEqual(response.status_code, 200)
        state = State.objects.get(pk=322)
        self.assertEqual(state.rank, 0)
        state = State.objects.get(pk=318)
        self.assertEqual(state.rank, 1)
        state = State.objects.get(pk=320)
        self.assertEqual(state.rank, 2)
        state = State.objects.get(pk=324)
        self.assertEqual(state.rank, 3)

    def test_add_set(self):
        response = self.client.post('/states/sets', {'name' : 'Brand new set'})
        self.assertEqual(response.status_code, 200)
        states_set = StatesSet.objects.latest('created_date')
        self.assertEqual(states_set.name, 'Brand new set')

    def test_add_state(self):
        response = self.client.post('/states/sets', {'name' : 'Brand new state', 'set_id' : '317', 'percentage' : '29'})
        self.assertEqual(response.status_code, 200)
        state = State.objects.latest('created_date')
        self.assertEqual(state.name, 'Brand new state')
        self.assertEqual(state.rank, 4)
        self.assertEqual(state.percentage, 29)
        
class KanbanTests(FormattedOutputTestCase):
    fixtures = ['kanban.json']

    def setUp(self):
        self.client = Client()
        self.client.login(username='owner1', password='owner1')

    def tearDown(self):
        self.client.logout()

    def test_simple_get_kanban(self):
        response = self.client.get('/states/show_kanban/68')
        self.assertEqual(response.status_code, 200)
        
    def test_states_for_project(self):
        response = self.client.get('/states/show_kanban/68')
        self.assertEqual(len(response.context['states']), 2)
        response = self.client.get('/states/show_kanban/474')
        self.assertEqual(len(response.context['states']), 0)
        
    def test_contents_count(self):
        response = self.client.get('/states/show_kanban/68')
        self.assertEqual(len(response.context['contents']), 14)
        response = self.client.get('/states/show_kanban/474')
        self.assertEqual(len(response.context['contents']), 1)
        
class KanbanCreatePresentationTests(FormattedOutputTestCase):
    fixtures = ['kanban_create_presentation.json']

    def setUp(self):
        super(KanbanCreatePresentationTests, self).setUp()
        self.client = Client()
        self.client.login(username='kgebert', password='kgebert1')

    def tearDown(self):
        super(KanbanCreatePresentationTests, self).tearDown()
        self.client.logout()       
            
    def test_new_presentation_in_first_state(self):
        response = self.client.post('/mycontent/addcontent/18?next=/corporate/list/18', { 'title' : 'testowa prezentacja' })
        self.assertEqual(response.status_code, 302)
        latest_content = Content.objects.all().latest('created_date')
        latest_content_state = ContentState.objects.all().latest('created_date')
        self.assertEqual(latest_content, latest_content_state.content)
        self.assertEqual(latest_content_state.state.rank, 0)
        
    def test_new_presentation_without_states_set(self):
        response = self.client.post('/mycontent/addcontent/20?next=/corporate/list/20', { 'title' : 'testowa prezentacja 2' })
        self.assertEqual(response.status_code, 302)
        latest_content_state = ContentState.objects.all()
        self.assertEqual(0, len(latest_content_state))
        
class NewKanbanTests(FormattedOutputTestCase):
    fixtures = ['new_kanban_states.json']

    def setUp(self):
        self.client = Client()
        self.client.login(username='owner1', password='owner1')

    def tearDown(self):
        self.client.logout()
        
    def test_display_correct_message(self):
        response = self.client.get('/states/change_to_ready/713/504?next=/states/show_kanban/68', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Presentation Chinese state changed from In progress to Ready')
        
        response = self.client.get('/states/change/769/538?next=/states/show_kanban/68', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Presentation Lukasz state changed from Stan 4 to Stan 5')
        
        response = self.client.get('/states/change/737/464?next=/states/show_kanban/68', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Presentation Rozowy state changed from Contents without state to Stan 1')
        
    def test_change_to_ready(self):
        response = self.client.get('/states/change_to_ready/713/504?next=/states/show_kanban/68')
        self.assertEqual(response.status_code, 302)
        state = State.objects.get(pk=504)
        content = Content.objects.get(pk=713)
        content_state = ContentState(state=state, content=content)
        self.assertEqual(content_state.is_current, False)
        
    def test_content_state_history(self):
        content = Content.objects.get(pk=133) # content in State 5 in Ready section
        content_states = ContentState.objects.filter(content=content)
        self.assertEqual(len(content_states), 5) # should have already 6 states created
        content_states_current = ContentState.objects.filter(is_current=True, content=content)
        self.assertEqual(len(content_states_current), 0) # all states have is current on False
        
        content = Content.objects.get(pk=777) # content in State 6 in In progress section
        content_states = ContentState.objects.filter(content=content)
        self.assertEqual(len(content_states), 6) # should have already 6 states created
        content_states_current = ContentState.objects.filter(is_current=True, content=content)
        self.assertEqual(len(content_states_current), 1) # only 1 state is current !
     
    def test_state_ready_and_in_progress(self):
        response = self.client.get('/states/show_kanban/68')
        self.assertEqual(response.status_code, 200)
        state = response.context['states'][1] # 2nd State
        self.assertEqual(state.name, 'Stan 2')
        self.assertEqual(len(response.context['contents']), 10) # 10 contents left in Contents without state
        self.assertEqual(len(state.contents_ready), 5) # contents ready
        self.assertEqual(len(state.contents), 6) # contents in progress
        
    def test_contents_count_when_two_projects_has_the_same_state_set(self):
        response = self.client.get('/states/show_kanban/474') # this project has the same state_set as project with id 68
        state = response.context['states'][0] # 1st State
        self.assertEqual(len(state.contents), 0) # contents in progress
        self.assertEqual(len(state.contents_ready), 1) # contents ready
        self.assertEqual(len(response.context['contents']), 1) # 10 contents left in Contents without state
    
        
    
        
        