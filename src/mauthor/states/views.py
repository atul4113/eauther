from django.views.generic.base import TemplateView
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required

from libraries.utility.helpers import get_object_or_none
from lorepo.token.models import TOKEN_KEYS
from lorepo.token.util import create_project_states_token, create_kanban_token
from lorepo.token.decorators import TokenMixin, cached_token
from mauthor.utility.decorators import company_admin, LoginRequiredMixin
from mauthor.states.models import StatesSet, State, StateToSet, ProjectStatesSet,\
    ContentState
from mauthor.states.forms import AddSetForm, AddStateForm, RenameStateForm
from lorepo.spaces.models import Space
from lorepo.mycontent.models import Content
from libraries.utility.redirect import get_redirect
from mauthor.states.util import get_states_sets
from lorepo.mycontent.util import get_contents_from_subspaces
from lorepo.spaces.util import filter_deleted, get_spaces_subtree
import libraries.utility.cacheproxy as cache

@login_required
@company_admin
def list_sets(request, set_id=None):
    add_set_form = AddSetForm()
    add_state_form = AddStateForm()
    edit_set_form = AddSetForm()

    if request.method == 'POST':
        if 'set_id' in request.POST:
            add_state_form = add_state(request)
        elif set_id:
            edit_set_form = edit_set(request, set_id)
        else:
            add_set_form = add_set(request)

    sets = StatesSet.objects.filter(company=request.user.company).order_by('name')
    if set_id is not None:
        states_to_set = [sts.state_id for sts in StateToSet.objects.filter(states_set__id=set_id)]
        states = State.objects.filter(id__in=states_to_set).order_by('rank')
        set_id = int(set_id)
        set = get_object_or_none(StatesSet, pk=set_id)
        if set:
            edit_set_form = AddSetForm({'name':set.name})
    else:
        states = []

    return render(request, 'states/list.html',
                  {
                   'sets' : sets,
                   'states' : states,
                   'add_set_form' : add_set_form,
                   'add_state_form' : add_state_form,
                   'edit_set_form' : edit_set_form,
                   'set_id' : set_id}
                  )

def add_set(request):
    form = AddSetForm(request.POST)
    if form.is_valid():
        states_set = StatesSet(name=form.cleaned_data['name'])
        states_set.company = request.user.company
        states_set.save()
        return AddSetForm()
    return form

def edit_set(request, set_id):
    form = AddSetForm(request.POST)
    if form.is_valid():
        set = get_object_or_404(StatesSet, pk=set_id)
        set.name = request.POST.get('name')
        set.save()
        messages.info(request, 'Set name changed')
    return form

def add_state(request):
    form = AddStateForm(request.POST)
    if form.is_valid():
        states_to_set = [sts.state_id for sts in StateToSet.objects.filter(states_set__id=form.cleaned_data['set_id'])]
        states = State.objects.filter(id__in=states_to_set).order_by('-rank')

        state = State(name=form.cleaned_data['name'], percentage=form.cleaned_data['percentage'])
        if states:
            state.rank = states[0].rank + 1
        else:
            state.rank = 0
        state.save()
        states_set = StatesSet.objects.get(pk=form.cleaned_data['set_id'])
        state_to_set = StateToSet(state=state, states_set=states_set)
        state_to_set.save()
        return AddStateForm()
    return form

@login_required
@company_admin
def update_rank(request, state_id, new_rank):
    state = get_object_or_404(State, pk=state_id)
    new_rank = int(new_rank)
    sts = StateToSet.objects.get(state=state)
    others = StateToSet.objects.filter(states_set=sts.states_set)
    for s in others:
        if new_rank > state.rank and s.state.rank <= new_rank and s.state.rank > state.rank:
            s.state.rank = s.state.rank - 1
            s.state.save()
        if new_rank < state.rank and s.state.rank >= new_rank and s.state.rank < state.rank:
            s.state.rank = s.state.rank + 1
            s.state.save()
    state.rank = new_rank
    state.save()
    return HttpResponse(content="OK")

@login_required
@company_admin
def update_percentage(request, state_id, percentage):
    state = get_object_or_404(State, pk=state_id)
    state.percentage = percentage
    state.save()
    return HttpResponse(content="OK")

@login_required
@company_admin
def delete_state(request, state_id):
    state = get_object_or_404(State, pk=state_id)
    del_state(state)
    messages.info(request, 'State removed')
    return get_redirect(request, '/states/sets')

def del_state(state):
    for sts in state.statetoset_set.all():
        sts.delete()
    for cs in state.contentstate_set.all():
        cs.delete()
    state.delete()

@login_required
@company_admin
def delete_set(request, set_id):
    set = get_object_or_404(StatesSet, pk=set_id)
    for sts in StateToSet.objects.filter(states_set=set):
        del_state(sts.state)
    ProjectStatesSet.objects.filter(states_set=set).delete()
    set.delete()
    messages.info(request, 'State set removed')
    return get_redirect(request, '/states/sets')

@login_required
@company_admin
def rename_state(request, state_id):
    state = get_object_or_404(State, pk=state_id)
    form = RenameStateForm()
    if request.method == 'POST':
        form = RenameStateForm(request.POST)
        if form.is_valid():
            state.name = form.cleaned_data['name']
            state.save()
            return get_redirect(request, '/states/sets')
    next_url = form.data['next'] if 'next' in form.data else request.GET.get('next')
    return render(request, 'states/rename.html', {'state' : state, 'form' : form, 'next' : next_url})


class ProjectStates(LoginRequiredMixin, TokenMixin, TemplateView):
    token_key = TOKEN_KEYS.PROJECT_STATES
    template_name = "states/project.html"
    methods = ["POST"]

    def get_data(self):
        project = get_object_or_404(Space, pk=self.kwargs["project_id"])
        project_states_set = ProjectStatesSet.objects.filter(project=project)

        return {
            "project": project,
            "project_states_set": project_states_set,
            "kanban": project_states_set[0] if len(project_states_set) == 1 else None,
            "kanban_sets": project_states_set
        }

    def get_context_data(self, **kwargs):
        states_sets = StatesSet.objects.filter(company=self.request.user.company)
        token, token_key = create_project_states_token(self.request.user)

        context = {
            'sets': sorted(states_sets, key=lambda states_set: states_set.name),
            'next': self.request.GET['next'] if 'next' in self.request.GET else None,
            'token_value': token,
            'token_key': token_key
        }

        context.update(self.get_data())
        return context

    def post(self, request, *args, **kwargs):
        data = self.get_data()
        self.remove_previous_kanban(data)
        self.set_new_kanban(request, data)

        return HttpResponseRedirect(request.POST['next'] if 'next' in request.POST else '/corporate')

    def remove_previous_kanban(self, data):
        data["kanban_sets"].delete()
        for content in get_contents_from_subspaces(data["project"]):
            content.contentstate_set.all().delete()

    def set_new_kanban(self, request, data):
        if request.POST['set_id']:
            kanban = StatesSet.objects.get(pk=request.POST['set_id'])
            new_kanban = ProjectStatesSet(project=data["project"], states_set=kanban)
            new_kanban.save()


@cached_token(TOKEN_KEYS.KANBAN)
@login_required
def change_state(request, content_id, state_id):
    content = Content.get_cached_or_404(id=content_id)
    cs = None
    if len(ContentState.objects.filter(content=content, is_current=False)) > 0:
        cs = ContentState.objects.filter(content=content, is_current=False).latest('modified_date')
    if cs:
        old_state = cs.state
        cs.is_current = False
        cs.save()
    else:
        old_state = 'Contents without state'
    state = get_object_or_404(State, pk=state_id)
    css = ContentState.objects.filter(content=content, state=state)
    if len(css) == 0:
        new_cs = ContentState(content=content, state=state)
        new_cs.is_current = True
        new_cs.save()
        messages.success(request, "Presentation %(content)s state changed from %(old_state)s to %(state)s" % locals() )
    else:
        messages.warning(request, "Content state has already been changed. Refreshing the page")
    cache.delete("content_state_%s" % content.id)
    return get_redirect(request, '/corporate')

@cached_token(TOKEN_KEYS.KANBAN)
@login_required
def change_to_ready(request, content_id, state_id):
    content = Content.get_cached_or_404(id=content_id)
    state = get_object_or_404(State, pk=state_id)
    css = ContentState.objects.filter(content=content, state=state, is_current=True)
    if len(css) == 1:
        css[0].is_current = False
        css[0].save()
        messages.success(request, "Presentation %(content)s state changed from In progress to Ready" % locals())
    else:
        messages.warning(request, "Content state has already been changed. Refreshing the page")
    cache.delete("content_state_%s" % content.id)
    return get_redirect(request, '/corporate')

@login_required
def show_kanban(request, project_id):
    project = get_object_or_404(Space, id = project_id)
    pss = ProjectStatesSet.objects.filter(project=project)
    if len(pss) == 1:
        sets = get_states_sets(request.user.company)
        project_set = sets[pss[0].states_set]
        project_set = sorted(project_set, key=lambda project_set: project_set.rank)
        for state in project_set:
            state.contents = set()
            state.contents_ready = set()
            index = project_set.index(state)
            state.next = None
            if index + 1 < len(project_set):
                state.next = project_set[index + 1]
    else:
        project_set = []
    contents_without_state = []
    project_contents, deleted, total = filter_deleted(get_spaces_subtree(project.id))
    for content in project_contents:
        content_states = ContentState.objects.filter(content=content).order_by('-created_date')
        if len(content_states) == 0:
            contents_without_state.append(content)
        else:
            latest_content_state = content_states[0]
            if project_set.count(latest_content_state.state):
                i = project_set.index(latest_content_state.state)
                if latest_content_state.is_current:
                    project_set[i].contents.add(content)
                else:
                    project_set[i].contents_ready.add(content)
    token, token_key = create_kanban_token(request.user)
    return render(request, 'states/show_kanban.html',
                  {
                   'project' : project,
                   'states' : project_set,
                   'contents' : contents_without_state,
                   'token': token,
                   'token_key': token_key,
                   })
