from src.libraries.utility.environment import get_versioned_module
import libraries.utility.queues

def update_index_async(*args, **kwargs):
    content_id = kwargs['content_id']
    libraries.utility.queues.trigger_backend_task('/search/put/%s' % content_id, target=get_versioned_module('localization'), queue_name='search')

def update_index_async_from_backend(*args, **kwargs):
    content_id = kwargs['content_id']
    libraries.utility.queues.trigger_backend_task('/search/put/%s' % content_id, target=get_versioned_module('localization'), queue_name='search')
