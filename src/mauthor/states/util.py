from mauthor.states.models import StatesSet, StateToSet, ContentState
import libraries.utility.cacheproxy as cache

def get_states_sets(company):
    states_set = {}
    for s_set in StatesSet.objects.filter(company=company):
        states = []
        for sts in StateToSet.objects.filter(states_set=s_set):
            states.append(sts.state)
        states_set[s_set] = sorted(states, key=lambda state: state.rank)
    return states_set

def get_current_state_for_content(content):
    cached = cache.get("content_state_%s" % content.id)
    if cached is not None:
        return cached[0], cached[1]
    content_states = ContentState.objects.filter(content=content).order_by('-created_date')
    if len(content_states) > 0:
        cache.set("content_state_%s" % content.id, (content_states[0].state, content_states[0].is_current), 60 * 60 * 24)
        return content_states[0].state, content_states[0].is_current
    else:
        return None, False